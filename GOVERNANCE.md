# Governance

## Project Roles

### Contributors

Individuals who want to contribute ideas to the TUF specification. Cleanups and
clarifications are discussed in [GitHub Issues](
https://github.com/theupdateframework/specification/issues)
and submitted as [GitHub Pull Requests](
https://github.com/theupdateframework/specification/pulls).

New ideas and enhancements to the specification are submitted through the [TUF
Augmentation Proposal (TAP) process](
https://github.com/theupdateframework/taps/blob/master/tap1.md).

### Consensus Builder

Ultimate authority for changes to the TUF specification, including changes
proposed through the [TAP process](
https://github.com/theupdateframework/taps/blob/master/tap1.md), falls to the
specification's Consensus Builder.

### TAP Editors

The TAP Editors are a team of core contributors to the TUF project who are
responsible for reviewing and approving, or rejecting, any proposed
[TAPs](https://github.com/theupdateframework/taps), and changes to the
specification.


## Change Review Process

__All changes must be submitted as a GitHub Pull Request (PR)__

The submitter of the PR is responsible for responding to feedback from
reviewers and maintainers. While the PR remains open the submitter is also
responsible for ensuring the change is in a state which can be merged.

__All minor changes must be approved by at least two (2) other TAP editors__

Obvious language correctness (grammar and typo fixes), or other changes that
do not significantly alter the specification must be approved by at least two
(2) TAP Editors. These minor changes do not require a contemplation period.

__All major changes must be approved by at least two (2) other TAP editors,
and merged no sooner than one (1) week after submission__

In order to ensure the security properties of TUF are maintained it is
necessary to contemplate how any changes to the specification may affect those
security properties. Therefore, all PRs containing non-minor changes will
remain open for at least one (1) week to allow all interested TAP Editors time
to review the submission.

A TAP editor may request longer to consider the changes, so long as that
request is made within the initial one (1) week contemplation period.

Non-minor changes to the specification require two (2) TAP editor approvals.

Major changes should not be merged when there are outstanding changes
requested. In cases where the requested changes are not agreeable to the
submitter, and therefore will not be made, the request for changes should be
revoked by the requesting TAP editor.
When consensus can not be agreed between submitter and TAP editors,
the Consensus Builder holds ultimate authority on whether to accept the
proposed change.
