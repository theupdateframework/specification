# TUF Roadmap

### Housekeeping

Which of these should block releases?
* Convert detailed client workflow to use sub-procedures
    * Goal: less repetition
    * Goal: easy to implement and map to the spec requirements (checklist like)
* Update specification tooling to do date and version bumping in GHA
* Implementations should catch up with spec-1.x.y
    * Resolution: implementations should explicitly list what they support
* Should implementations refactor their code before implementing new TAPs?
    * Resolution: up to implementations to define what they want to do

## Goals for upcoming releases

### Minor releases

* [TAP 4: Multiple repository consensus on trusted targets](https://github.com/theupdateframework/taps/blob/master/tap4.md) (likely to be much easier if the client-workflow -> sub-procedures change is done first)
* [TAP 15: Succinct hashed bin delegations](https://github.com/theupdateframework/taps/blob/master/tap15.md) (needs implementation & approval)
* [TAP 13: User Selection of the Top-Level Target Files Through Mapping Metadata](https://github.com/theupdateframework/taps/pull/118) (needs accepting as draft, implementation & approval)
* [TAP 16: Snapshot Merkle trees](https://github.com/theupdateframework/taps/blob/master/tap16.md) (needs implementation & approval)

### Major releases

* [TAP 3: Multi-role delegations](https://github.com/theupdateframework/taps/blob/master/tap3.md) (also likely to be easier if client-workflow refactor done first)
* [TAP 8: Key rotation and explicit self-revocation](https://github.com/theupdateframework/taps/blob/master/tap8.md) (needs implementation & approval)
* [TAP 14: Managing TUF versions](https://github.com/theupdateframework/taps/blob/master/tap14.md) (needs implementation & approval)
* [TAP X: DSSE](https://github.com/theupdateframework/taps/pull/138) (needs accepting as draft, implementation and approval)

### Timeline (2022)
* Specification refactor by June
* TAP 15 Accepted & in reference implementation by June
* TAP 15 in the spec by end of year
* TAP 3 & 4, work on implementations
* Implement TAP 13 in go-tuf
* All implementations should catch up to 1.x.y by $MONTH and $DATE?

## Implementation roadmaps

The following are links to roadmaps for various TUF implementations. These roadmaps are maintained by the projects. If you have a TUF implementation, feel free to open a pr to add it here.

* **python-tuf**: 
* **go-tuf**: https://github.com/orgs/theupdateframework/projects/3
* ...
