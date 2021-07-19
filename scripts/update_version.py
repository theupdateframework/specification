"""
<Program Name>
  make_release.py

<Author>
  Lukas Puehringer <lukas.puehringer@nyu.edu>
  Joshua Lock <jlock@vmware.com>

<Started>
  Jan 3, 2020

<Copyright>
  See LICENSE for licensing information.

<Purpose>
  Set the version number and date according to the versioning requirements in
  README.rst.

  Expects GitHub Actions environment variables:
  - GITHUB_REF        the ref that triggered the workflow (i.e refs/pull/33/merge)
  - GITHUB_BASE_REF   the target branch (usually master)
  - GITHUB_HEAD_REF   the name of the submitters branch
    (see https://docs.github.com/en/free-pro-team@latest/actions/reference/environment-variables)
"""
import os
import re
import sys
import shlex
import datetime
import shutil
import subprocess
import tempfile

SPEC_NAME = "tuf-spec.md"

LAST_MODIFIED_PATTERN = "Date: %Y-%m-%d\n"
LAST_MODIFIED_LINENO = 6

VERSION_PATTERN = r"^Text Macro: VERSION (\d*)\.(\d*)\.(\d*)$"
VERSION_LINENO = 19

class SpecError(Exception):
  """Common error message part. """
  def __init__(self, msg):
    super().__init__(
        msg + ", please see 'Versioning' section in README.rst for details.")


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

  # Only proceed if the spec itself was changed
  # git_run = subprocess.run(shlex.split(
  #   "git diff --name-only origin/master {}".format(current_branch)),
  #                          capture_output=True, check=True, text=True)
  # modified_files = git_run.stdout.split() or []

  # if SPEC_NAME not in modified_files:
  #   print("*"*68)
  #   print("{} not modified, skipping version and date check.".format(SPEC_NAME))
  #   print("*"*68)
  #   return 1

  # Read the first few lines from the previous specification document and
  # extract date and version from spec file header in the master branch
  spec_head = get_spec_head()
  date_prev = get_date(spec_head).strftime("%Y-%m-%d")
  version_prev = get_version(spec_head)

  # Make the version bump type depending on the PR originating branch
  # - if the originating branch is 'draft', it is minor bump
  # - otherwise, it must be a patch bump
  if os.environ["GITHUB_BASE_REF"] == "draft":
    version_new = "{}.{}.{}".format(version_prev[0], version_prev[1] + 1, 0)
  else:
    version_new = "{}.{}.{}".format(version_prev[0], version_prev[1], version_prev[2] + 1)

  date_new = datetime.date.today().strftime("%Y-%m-%d")

  version_prev_fmt = "{}.{}.{}".format(version_prev[0], version_prev[1], version_prev[2])
  print("Replacing old version ({}) with new version: {}".format(version_prev_fmt, version_new))
  print("Replacing old date ({}) with new date: {}".format(date_prev, date_new))

  with open(SPEC_NAME) as spec:
      fh, tmp_file = tempfile.mkstemp()
      lineno = 1
      with os.fdopen(fh, "w") as new_file:
        for line in spec:
          if lineno == VERSION_LINENO:
            new_file.write(line.replace(version_prev_fmt, version_new))
          elif lineno == LAST_MODIFIED_LINENO:
            new_file.write(line.replace(date_prev, date_new))
          else:
            new_file.write(line)
          lineno = lineno + 1

  shutil.copymode(SPEC_NAME, tmp_file)
  os.remove(SPEC_NAME)
  shutil.move(tmp_file, SPEC_NAME)
  return 0


if __name__ == '__main__':
  sys.exit(main())
