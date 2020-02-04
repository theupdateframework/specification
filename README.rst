The Update Framework specification
----------------------------------

- `latest stable <https://github.com/theupdateframework/specification/blob/master/tuf-spec.md>`_
- `current draft <https://github.com/theupdateframework/specification/blob/draft/tuf-spec.md>`_
- `new changes since latest stable <https://github.com/theupdateframework/specification/compare/master..draft>`_
- `release history <https://github.com/theupdateframework/specification/tags>`_


Contact
-------

Please contact us via our `mailing list
<https://groups.google.com/forum/?fromgroups#!forum/theupdateframework>`_.

Questions, feedback, and suggestions are welcomed on this low volume mailing
list.  We strive to make the specification easy to implement, so if you come
across any inconsistencies or experience any difficulty, do let us know by
sending an email, or by reporting an issue in the `specification repo
<https://github.com/theupdateframework/specification/issues>`_.


License
-------

This work is `dual-licensed <https://en.wikipedia.org/wiki/Multi-licensing>`_
and distributed under the (1) MIT License and (2) Apache License, Version 2.0.
Please see `LICENSE-MIT.txt
<https://github.com/theupdateframework/specification/blob/master/LICENSE-MIT.txt>`_
and `LICENSE-APACHE.txt
<https://github.com/theupdateframework/specification/blob/master/LICENSE-APACHE.txt>`_.

Versioning
----------

The TUF specification uses `Semantic Versioning 2.0.0 <https://semver.org/>`_
(semver) for its version numbers, and a gitflow-based release management:

- The 'master' branch of this repository always points to the latest stable
  version of the specification.
- The 'draft' branch of this repository always points to the latest development
  version of the specification and must always be based off of the latest
  'master' branch.
- Contributors must submit changes as pull requests against these branches,
  depending on the type of the change (see semver rules).
- For patch-type changes, pull requests may be submitted directly against the
  'master' branch.
- For major- and minor-type changes, pull requests must be submitted against
  the 'draft' branch.
- Maintainers may, from time to time, decide that the 'draft' branch is ready
  for a new major or minor release, and submit a pull request from 'draft'
  against 'master'.
- Before merging a branch with 'master' the 'last modified date' and 'version'
  in the specification header must be bumped.
- Merges with 'master' that originate from the 'draft' branch must bump either
  the major or minor version number.
- Merges with 'master' that originate from any other branch must bump the patch
  version number.
- Merges with 'master' must be followed by a git tag for the new version
  number.
- Merges with 'master' must be followed by a rebase of 'draft' onto 'master'.



Acknowledgements
----------------

This project is managed by the Linux Foundation under the Cloud Native
Computing Foundation. The consensus builder for the TUF specification is
`Prof. Justin Cappos <https://ssl.engineering.nyu.edu/personalpages/jcappos/>`_
of the `Secure Systems Lab <https://ssl.engineering.nyu.edu/>`_ at
`New York University <https://engineering.nyu.edu>`_. Maintainers include
`Sebastien Awwad <https://github.com/awwad>`_ of
`CONDA <https://docs.conda.io/en/latest/>`_ and
`Lukas Pühringer <https://github.com/lukpueh/>`_ of
`NYU's Secure Systems Lab <https://ssl.engineering.nyu.edu/>`_. Contributors
and maintainers are governed by the
`CNCF Community Code of Conduct <https://github.com/cncf/foundation/blob/master/code-of-conduct.md>`_.

We'd like to thank
Justin Samuel, Roger Dingledine, Nick Matthewson, Trishank Karthik Kuppusamy, and
all of the TAP authors for their contributions to the TUF spec.

This material is based upon work supported by the National Science Foundation
under Grant Nos. CNS-1345049 and CNS-0959138. Any opinions, findings, and
conclusions or recommendations expressed in this material are those of the
author(s) and do not necessarily reflect the views of the National Science
Foundation.
