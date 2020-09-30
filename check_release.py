"""
<Program Name>
  check_release.py

<Author>
  Lukas Puehringer <lukas.puehringer@nyu.edu>

<Started>
  Jan 3, 2020

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Check that specification updates are performed according to the versioning
  requirements in README.rst.

  Expects Travis environment variables:
  - TRAVIS_BRANCH
  - TRAVIS_PULL_REQUEST_BRANCH
  (see https://docs.travis-ci.com/user/environment-variables/)

"""
import os
import re
import sys
import shlex
import datetime
import subprocess

SPEC_NAME = "tuf-spec.md"

LAST_MODIFIED_PATTERN = "Last modified: **%d %B %Y**\n"
LAST_MODIFIED_LINENO = 3

VERSION_PATTERN = r"^Version: \*\*(\d*)\.(\d*)\.(\d*)\*\*$"
VERSION_LINENO = 5

class SpecError(Exception):
  """Common error message part. """
  def __init__(self, msg):
    super().__init__(
        msg + " please see 'Versioning' section in README.rst for details.")


def get_spec_head():
  """Return the lines (as list) at the head of the file that contain last date
  modified and version. """
  with open(SPEC_NAME) as spec_file:
    spec_head = [next(spec_file)
        for x in range(max(VERSION_LINENO, LAST_MODIFIED_LINENO))]

  return spec_head


def get_date(spec_head):
  """Parse date from spec head and return datetime object. """
  last_modified_line = spec_head[LAST_MODIFIED_LINENO - 1]

  try:
    date = datetime.datetime.strptime(last_modified_line,
        LAST_MODIFIED_PATTERN)

  except ValueError as e:
    raise SpecError("expected to match '{}' (datetime format) in line {}, but"
        " got '{}': {}.".format(LAST_MODIFIED_PATTERN, LAST_MODIFIED_LINENO,
        last_modified_line, e))

  return date


def get_version(spec_head):
  """Parse version from spec head and return (major, minor, patch) tuple. """
  version_line = spec_head[VERSION_LINENO - 1]

  version_match = re.search(VERSION_PATTERN, version_line)
  if not version_match:
    raise SpecError("expected to match '{}' (regex) in line {}, but got '{}'."
        .format(VERSION_PATTERN, VERSION_LINENO, version_line))

  major, minor, patch = version_match.groups()
  return int(major), int(minor), int(patch)


def main():
  """Check that the current branch is based off of the master branch and that
  the last modified date and version number in the specification document
  header are higher than in the master branch, i.e. were bumped. """

  # Skip version and date comparison on push builds ...
  # As per https://docs.travis-ci.com/user/environment-variables/
  #   if the current job is a push build, this [env] variable is empty ("")
  if not os.environ.get("TRAVIS_PULL_REQUEST_BRANCH"):
    print("skipping version and date check for non pr builds ...")
    sys.exit(0)

  # ... also skip on PRs that don't target the master branch
  # As per https://docs.travis-ci.com/user/environment-variables/:
  #   for builds triggered by a pull request this [env variable] is the name of
  #   the branch targeted by the pull request
  if not os.environ.get("TRAVIS_BRANCH") == "master":
    print("skipping version and date for builds that don't target master ...")
    sys.exit(0)

  # Check that the current branch is based off of the master branch
  try:
    subprocess.run(
        shlex.split("git merge-base --is-ancestor master {}".format(
        os.environ["TRAVIS_PULL_REQUEST_BRANCH"])), check=True)

  except subprocess.CalledProcessError as e:
    raise SpecError("make sure the current branch is based off of master")

  # Read the first few lines from the updated specification document and
  # extract date and version from spec file header in the current branch
  spec_head = get_spec_head()
  date_new = get_date(spec_head)
  version_new = get_version(spec_head)

  # Checkout master branch
  subprocess.run(shlex.split("git checkout -q master"), check=True)

  # Read the first few lines from the previous specification document and
  # extract date and version from spec file header in the master branch
  spec_head = get_spec_head()
  date_prev = get_date(spec_head)
  version_prev = get_version(spec_head)

  # Assert date update
  if not (date_new > date_prev or
      date_new.date() == date_prev.date() == datetime.date.today()):
    raise SpecError("new 'last modified date' ({:%d %B %Y}) must be greater"
        " than the previous one ({:%d %B %Y}) or both must be today.".format(
        date_new, date_prev))

  # Assert version bump type depending on the PR originating branch
  # - if the originating branch is 'draft', it must be a major (x)or minor bump
  # - otherwise, it must be a patch bump
  if os.environ["TRAVIS_PULL_REQUEST_BRANCH"] == "draft":
    if not (((version_new[0] > version_prev[0]) !=
        (version_new[1] > version_prev[1])) and
        (version_new[2] == version_prev[2])):
      raise SpecError("new version ({}) must have exactly one of a greater"
        " major or a greater minor version number than the previous one ({}),"
        " if the PR originates from the 'draft' branch.".format(version_new,
        version_prev))

  else:
    if not (version_new[:2] == version_prev[:2] and
        version_new[2] > version_prev[2]):
      raise SpecError("new version ({}) must have exactly a greater patch"
          " version number than the previous one ({}), if the PR originates"
          " from a feature branch (i.e. not 'draft')".format(version_new,
          version_prev))

  print("*"*68)
  print("thanks for correctly bumping version and last modified date. :)")
  print("don't forget to tag the release and to sync 'draft' with master!! :P")
  print("*"*68)


if __name__ == '__main__':
  main()