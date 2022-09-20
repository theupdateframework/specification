<pre class='metadata'>
Title: The Update Framework Specification
Shortname: TUF
Status: LS
Abstract: A framework for securing software update systems.
Date: 2022-09-09
Editor: Justin Cappos, NYU
Editor: Trishank Karthik Kuppusamy, Datadog
Editor: Joshua Lock, VMware
Editor: Marina Moore, NYU
Editor: Lukas Pühringer, NYU
Repository: theupdateframework/specification
Mailing List: https://groups.google.com/forum/?fromgroups#!forum/theupdateframework
Indent: 2
Boilerplate: copyright no, conformance no
Local Boilerplate: header yes
Markup Shorthands: css no, markdown yes
Metadata Include: This version off, Abstract off
Text Macro: VERSION 1.0.31
</pre>

Note: We strive to make the specification easy to implement, so if you come
across any inconsistencies or experience any difficulty, do let us know by
sending an email to our [mailing list](
  https://groups.google.com/forum/?fromgroups#!forum/theupdateframework),
or by reporting an issue in the [specification repo](
  https://github.com/theupdateframework/specification/issues).


# Introduction # {#introduction}

## Scope ## {#scope}

This document describes a framework for securing software update systems.

The keywords "MUST," "MUST NOT," "REQUIRED," "SHALL," "SHALL NOT," "SHOULD,"
"SHOULD NOT," "RECOMMENDED," "MAY," and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

## Motivation ## {#motivation}

Software is commonly updated through software update systems.  These systems
can be package managers that are responsible for all of the software that is
installed on a system, application updaters that are only responsible for
individual installed applications, or software library managers that install
software that adds functionality such as plugins or programming language
libraries.

Software update systems all have the common behavior of downloading files
that identify whether updates exist and, when updates do exist, downloading
the files that are required for the update.  For the implementations
concerned with security, various integrity and authenticity checks are
performed on downloaded files.

Software update systems are vulnerable to a variety of known attacks.  This
is generally true even for implementations that have tried to be secure.

## History and credit ## {#history-and-credit}

Work on TUF began in late 2009.  The core ideas are based off of previous
work done by Justin Cappos and Justin Samuel that [identified security flaws
in all popular Linux package managers](https://theupdateframework.io/papers/attacks-on-package-managers-ccs2008.pdf).
More information and current versions of this document can be found at
[https://theupdateframework.io/](https://theupdateframework.io/)

The [Global Environment for Network Innovations](https://www.geni.net/) (GENI)
and the [National Science Foundation](https://www.nsf.gov/) (NSF) have
provided support for the development of TUF.

TUF's reference implementation is based on prior work on
[Thandy](https://www.torproject.org/), the application
updater for Tor. Its design and this spec
also came from ideas jointly developed in discussion with Thandy's authors.
The Thandy spec can be found at
[https://gitweb.torproject.org/thandy.git/tree/specs/thandy-spec.txt
](https://gitweb.torproject.org/thandy.git/tree/specs/thandy-spec.txt)

Whereas Thandy is an application updater for an individual software project,
TUF aims to provide a way to secure any software update system. We're very
grateful to the Tor Project and the Thandy developers for the early discussion
that led to the ideas in Thandy and TUF. Thandy is the hard
work of Nick Mathewson, Sebastian Hahn, Roger Dingledine, Martin Peck, and
others.

## Non-goals ## {#non-goals}

We are not creating a universal update system, but rather a simple and
flexible way that applications can have high levels of security with their
software update systems.  Creating a universal software update system would
not be a reasonable goal due to the diversity of application-specific
functionality in software update systems and the limited usefulness that
such a system would have for securing legacy software update systems.

We won't be defining package formats or even performing the actual update
of application files.  We will provide the simplest mechanism possible that
remains easy to use and provides a secure way for applications to obtain and
verify files being distributed by trusted parties.

We are not providing a means to bootstrap security so that arbitrary
installation of new software is secure.  In practice this means that people
still need to use other means to verify the integrity and authenticity of
files they download manually.

The framework will not have the responsibility of deciding on the correct
course of action in all error situations, such as those that can occur when
certain attacks are being performed.  Instead, the framework will provide
the software update system the relevant information about any errors that
require security decisions which are situation-specific.  How those errors
are handled is up to the software update system.

## Goals ## {#goals}

We need to provide a framework (a set of libraries, file formats, and
utilities) that can be used to secure new and existing software update
systems.

The framework should enable applications to be secure from all known attacks
on the software update process.  It is not concerned with exposing
information about what software is being updated (and thus what software
the client may be running) or the contents of updates.

The framework should provide means to minimize the impact of key compromise.
To do so, it must support roles with multiple keys and threshold/quorum
trust (with the exception of minimally trusted roles designed to use a
single key).  The compromise of roles using highly vulnerable keys should
have minimal impact.  Therefore, online keys (keys which are used in an
automated fashion) must not be used for any role that clients ultimately
trust for files they may install.

The framework must be flexible enough to meet the needs of a wide variety of
software update systems.

The framework must be easy to integrate with software update systems.

### Goals for implementation ### {#goals-for-implementation}

+ The client side of the framework must be straightforward to implement in any
  programming language and for any platform with the requisite networking and
  crypto support.

+ The process by which developers push updates to the repository must be
  simple.

+ The framework must be secure to use in environments that lack support for
  SSL (TLS).  This does not exclude the optional use of SSL when available,
  but the framework will be designed without it.

### Goals to protect against specific attacks ### {#goals-to-protect-against-specific-attacks}

Note: When saying the framework protects against an attack, it means the
attack will be unsuccessful.  It does not mean that a client will always
successfully update during an attack.  Fundamentally, an attacker
positioned to intercept and modify a client's communication can always
perform a denial of service.  Nevertheless, the framework must detect
when a client is unable to update.

+ **Arbitrary installation attacks.** An attacker cannot install anything
  they want on the client system. That is, an attacker cannot provide
  arbitrary files in response to download requests.

+ **Endless data attacks.**  An attacker cannot respond to client
  requests with huge amounts of data (extremely large files) that interfere
  with the client's system.

+ **Extraneous dependencies attacks.**  An attacker cannot cause clients
  to download or install software dependencies that are not the intended
  dependencies.

+ **Fast-forward attacks.**  An attacker cannot arbitrarily increase the
  version numbers of metadata files, listed in the snapshot metadata, well
  beyond the current value and thus tricking a software update system into
  thinking any subsequent updates are trying to rollback the package to a
  previous, out-of-date version.  In some situations, such as those where
  there is a maximum possible version number, the perpetrator cannot use a
  number so high that the system would never be able to match it with the
  one in the snapshot metadata, and thus new updates could never be
  downloaded.

+ **Indefinite freeze attacks.**  An attacker cannot respond to client
  requests with the same, outdated metadata without the client being aware
  of the problem.

+ **Malicious mirrors preventing updates.**  A repository mirror cannot
  prevent updates from good mirrors.

+ **Mix-and-match attacks.**  An attacker cannot trick clients into using
  a combination of metadata that never existed together on the repository
  at the same time.

+ **Rollback attacks.**  An attacker cannot trick clients into installing
  software that is older than that which the client previously knew to be
  available.

+ **Vulnerability to key compromises.** An attacker, who is able to
  compromise a single key or less than a given threshold of keys, cannot
  compromise clients.  This includes compromising a single online key (such
  as only being protected by SSL) or a single offline key (such as most
  software update systems use to sign files).

+ **Wrong software installation.**  An attacker cannot provide a file
  (trusted or untrusted) that is not the one the client wanted.

### Goals for PKI (Public key infrastructure) ### {#goals-for-pki}

* Software update systems using the framework's client code interface should
  never have to directly manage keys.

* All keys must be easily and safely revocable.  Trusting new keys for a role
  must be easy.

* For roles where trust delegation is meaningful, a role should be able to
  delegate full or limited trust to another role.

* The root of trust must not rely on external PKI.  That is, no authority will
  be derived from keys outside of the framework.

### TUF Augmentation Proposal (TAP) support ### {#tuf-augmentation-proposal-tap-support}

This major version (1.x.y) of the specification adheres to the following TAPs:

- [TAP 6](https://github.com/theupdateframework/taps/blob/master/tap6.md):
    Include specification version in metadata
- [TAP 9](https://github.com/theupdateframework/taps/blob/master/tap9.md):
    Mandatory Metadata signing schemes
- [TAP 10](https://github.com/theupdateframework/taps/blob/master/tap10.md):
    Remove native support for compressed metadata
- [TAP 11](https://github.com/theupdateframework/taps/blob/master/tap11.md):
    Using POUFs for Interoperability

Implementations compliant with this major version (1.x.y) of the specification
must also comply with the TAPs mentioned above.

# System overview # {#system-overview}

The framework ultimately provides a secure method of obtaining trusted
files.  To avoid ambiguity, we will refer to the files the framework is used
to distribute as "target files".  Target files are opaque to the framework.
Whether target files are packages containing multiple files, single text
files, or executable binaries is irrelevant to the framework.

The metadata describing target files is the information necessary to
securely identify the file and indicate which roles are trusted to provide
the file.  As providing additional information about
target files may be important to some software update systems using the
framework, additional arbitrary information can be provided with any target
file. This information will be included in signed metadata that describes
the target files.

The following are the high-level steps of using the framework from the
viewpoint of a software update system using the framework.  This is an
error-free case.

  : Polling
  ::
      Periodically, the software update system using the framework
      instructs the framework to check each repository for updates.  If
      the framework reports to the application code that there are
      updates, the application code determines whether it wants to
      download the updated target files.  Only target files that are
      trusted (referenced by properly signed and timely metadata) are
      made available by the framework.

  : Fetching
  ::
      For each file that the application wants, it asks the framework to
      download the file.  The framework downloads the file and performs
      security checks to ensure that the downloaded file is exactly what
      is expected according to the signed metadata.  The application code
      is not given access to the file until the security checks have been
      completed.  The application asks the framework to copy the
      downloaded file to a location specified by the application.  At
      this point, the application has securely obtained the target file
      and can do with it whatever it wishes.

## Roles and PKI ## {#roles-and-pki}

In the discussion of roles that follows, it is important to remember that
the framework has been designed to allow a large amount of flexibility for
many different use cases.  For example, it is possible to use the framework
with a single key that is the only key used in the entire system.  This is
considered to be insecure but the flexibility is provided in order to meet
the needs of diverse use cases.

There are four fundamental top-level roles in the framework:
- Root role
- Targets role
- Snapshot role
- Timestamp role

There is also one optional top-level role:
- Mirrors role

All roles can use one or more keys and require a threshold of signatures of
the role's keys in order to trust a given metadata file.

### Root role ### {#root}

The root role delegates trust to specific keys trusted for all other
top-level roles used in the system.

The client-side of the framework MUST ship with trusted root keys for each
configured repository.

The root role's private keys MUST be kept very secure and thus should be
kept offline.  If less than a threshold of Root keys are compromised, the
repository should revoke trust on the compromised keys.  This can be
accomplished with a normal rotation of root keys, covered in section
[[#key-management-and-migration]]. If a threshold of root keys is compromised,
the Root keys should be updated out-of-band, however, the threshold should
be chosen so that this is extremely unlikely.  In the unfortunate event that
a threshold of keys are compromised, it is safest to assume that attackers
have installed malware and taken over affected machines.  For this reason,
making it difficult for attackers to compromise all of the offline keys is
important because safely recovering from it is nearly impossible.


### Targets role ### {#targets}

The targets role's signature indicates which target files are trusted by
clients.  The targets role signs metadata that describes these files, not
the actual target files themselves.

In addition, the targets role can delegate full or partial trust to other
roles.  Delegating trust means that the targets role indicates another role
(that is, another set of keys and the threshold required for trust) is
trusted to sign target file metadata.  Partial trust delegation is when the
delegated role is only trusted for some of the target files that the
delegating role is trusted for.

Delegated roles can further delegate trust to other delegated
roles.  This provides for multiple levels of trust delegation where each
role can delegate full or partial trust for the target files they are
trusted for.  The delegating role in these cases is still trusted.  That is,
a role does not become untrusted when it has delegated trust.

Any delegation can be revoked at any time: the delegating role needs only
to sign new metadata that no longer contains that delegation.

### Snapshot role ### {#snapshot}

The snapshot role signs a metadata file that provides information about
the latest version of all targets metadata on the repository
(the top-level targets role and all delegated roles).  This information allows
clients to know which metadata files have been updated and also prevents
mix-and-match attacks.

### Timestamp role ### {#timestamp}

To prevent an adversary from replaying an out-of-date signed metadata file
whose signature has not yet expired, an automated process periodically signs
a timestamped statement containing the hash of the snapshot file.  Even
though this timestamp key must be kept online, the risk posed to clients by
the compromise of this key is minimal.

### Mirrors role ### {#mirrors}

Every repository has one or more mirrors from which files can be downloaded
by clients.  A software update system using the framework may choose to
hard-code the mirror information in their software or they may choose to use
mirror metadata files that can optionally be signed by a mirrors role.

The importance of using signed mirror lists depends on the application and
the users of that application.  There is minimal risk to the application's
security from being tricked into contacting the wrong mirrors.  This is
because the framework has very little trust in repositories.

## Threat model and analysis ## {#threat-model-and-analysis}

We assume an adversary who can respond to client requests, whether by acting
as a man-in-the-middle or through compromising repository mirrors.  At
worst, such an adversary can deny updates to users if no good mirrors are
accessible.  An inability to obtain updates is noticed by the framework.

If an adversary compromises enough keys to sign metadata, the best that can
be done is to limit the number of users who are affected.  The level to
which this threat is mitigated is dependent on how the application is using
the framework.  This includes whether different keys have been used for
different signing roles.

A detailed threat analysis is outside the scope of this document.  This is
partly because the specific threat posted to clients in many situations is
largely determined by how the framework is being used.

## Protocol, Operations, Usage, and Format (POUF) documents ## {#pouf-documents}

This specification purposefully leaves many implementation details,
including the metadata file formats, to the discretion of individual
implementations. These details do not affect the security of an
implementation, and so leaving them out of the specification allows this
document to support a greater variety of users. TUF implementers are
encouraged to document the wireline format and design decisions used in
their implementation as a POUF document. POUFs, as described in
[TAP 11](https://github.com/theupdateframework/taps/blob/master/tap11.md),
allow different adopters to create interoperable implementations of TUF.
POUFs should follow the layout described in TAP 11 and may be made
publicly available in the [TAP directory](https://github.com/theupdateframework/taps/tree/master/POUFs).

# The repository # {#the-repository}

An application uses the framework to interact with one or more repositories.
A repository is a conceptual source of target files of interest to the
application.  Each repository MAY have one or more mirrors as the
providers of files to be downloaded.  For example, each mirror may specify a
different host where files can be downloaded from over HTTP.

The mirrors can be full or partial mirrors as long as the application-side
of the framework can ultimately obtain all of the files it needs.  A mirror
is a partial mirror if it is missing files that a full mirror should have.
If a mirror is intended to only act as a partial mirror, the metadata and
target paths available from that mirror can be specified.

Roles, trusted keys, and target files are completely separate between
repositories.  A multi-repository setup is a multi-root system.  When an
application uses the framework with multiple repositories, the framework
does not perform any "mixing" of the trusted content from each repository.
It is up to the application to determine the significance of the same or
different target files provided from separate repositories.

## Repository layout ## {#repository-layout}

The filesystem layout in the repository is used for two purposes:
- To give mirrors an easy way to mirror only some of the repository.
- To specify which parts of the repository a given role has authority
  to sign/provide.

### Target files ### {#target-files}

The filenames and the directory structure of target files available from
a repository are not specified by the framework.  The names of these files
and directories are completely at the discretion of the application using
the framework.

However, when <a>CONSISTENT_SNAPSHOT</a>s are in use, there is a RECOMMENDED
mechanism for naming target files on the repository (see
[[#consistent-snapshots]]). If an application using the framework does not
follow these recommendations, but wishes to support self-contained consistent
snapshots the application MUST ensure that target files are persisted in a way
where each target file can be uniquely and consistently addressed.

### Metadata files ### {#metadata-files}

The filenames and directory structure of repository metadata are strictly
defined.  All metadata filenames will have an extension (EXT) based on the
metaformat, for example JSON metadata files would have an EXT of json.
The following are the metadata files of top-level roles relative
to the base URL of metadata available from a given repository mirror.

  : /root.EXT
  ::
    Signed by the root keys; specifies trusted keys for the other
    top-level roles.

  : /snapshot.EXT
  ::
    Signed by the snapshot role's keys.  Lists the version numbers of all
    target metadata files: the top-level targets.EXT and all delegated
    roles.

  : /targets.EXT
  ::
    Signed by the target role's keys.  Lists hashes and sizes of target
    files. Specifies delegation information and trusted keys for delegated
    target roles.

  : /timestamp.EXT
  ::
    Signed by the timestamp role's keys.  Lists hash(es), size, and version
    number of the snapshot file.  This is the first and potentially only
    file that needs to be downloaded when clients poll for the existence
    of updates.

  : /mirrors.EXT (optional)
  ::
    Signed by the mirrors role's keys.  Lists information about available
    mirrors and the content available from each mirror.

#### Metadata files for targets delegation #### {#metadata-files-for-targets-delegation}

When the targets role delegates trust to other roles, each delegated role
provides one signed metadata file.  As is the case with the directory
structure of top-level metadata, the delegated files are relative to the
base URL of metadata available from a given repository mirror.

A delegated role file is located at:

  : /DELEGATED_ROLE.EXT
  ::
    Where DELEGATED_ROLE is the name of the delegated role that has been
    specified in targets.EXT.  If this role further delegates trust to a role
    named ANOTHER_ROLE, that role's signed metadata file is made available at:

  : /ANOTHER_ROLE.EXT
  ::
    Delegated target roles are authorized by the keys listed in the directly
    delegating target role.

# Document formats # {#document-formats}

All of the formats described below include the ability to add more
attribute-value fields to objects for backwards-compatible format changes.
Implementers who encounter undefined attribute-value pairs in the format
must include the data when calculating hashes or verifying signatures and must
preserve the data when re-serializing. If a backwards incompatible format change
is needed, a new filename can be used.

## Metaformat ## {#metaformat}

Implementers of TUF may use any data format for metadata files as long as
all fields in this specification are included and TUF clients are able to
interpret them without ambiguity. Implementers should choose a data format
that allows for canonicalization, or one that will decode data
deterministically by default so that signatures can be accurately verified.
The chosen data format should be documented in the POUF of the implementation.
The examples in this document use a subset of the JSON object format, with
floating-point numbers omitted.  When calculating the digest of an
object, we use the "canonical JSON" subdialect as described at [Canonical JSON](
http://wiki.laptop.org/go/Canonical_JSON).

## File formats: general principles ## {#file-formats-general-principles}

All signed metadata objects have the format:

<pre highlight="json">
{
  "signed" : <a for="role">ROLE</a>,
  "signatures" : [
    { "keyid" : <a for="role">KEYID</a>,
      "sig" : <a>SIGNATURE</a> }
      , ... ]
}
</pre>

      : <dfn for="role">ROLE</dfn>
      ::
        A dictionary whose "_type" field describes the role type.

      : <dfn for="role">KEYID</dfn>
      ::
        The identifier of the key signing the <a for="role">ROLE</a> object,
        which is a hexdigest of the SHA-256 hash of the canonical form of the key.
        The keyid MUST be unique in the "signatures" array: multiple
        signatures with the same keyid are not allowed.

      : <dfn>SIGNATURE</dfn>
      ::
        A hex-encoded signature of the canonical form of the metadata for <a for="role">ROLE</a>.


All <dfn>KEY</dfn>s have the format:

<pre highlight="json">
{
  "keytype" : <a>KEYTYPE</a>,
  "scheme" : <a>SCHEME</a>,
  "keyval" : <a>KEYVAL</a>
}
</pre>

      : <dfn>KEYTYPE</dfn>
      ::
        A string denoting a public key signature system, such as <a
        for="keytype">"rsa"</a>, <a for="keytype">"ed25519"</a>, and <a
        for="keytype">"ecdsa-sha2-nistp256"</a>.

      : <dfn>SCHEME</dfn>
      ::
        A string denoting a corresponding signature scheme.  For example: <a
        for="scheme">"rsassa-pss-sha256"</a>, <a for="scheme">"ed25519"</a>, and <a
        for="scheme">"ecdsa-sha2-nistp256"</a>.

      : <dfn>KEYVAL</dfn>
      ::
        A dictionary containing the public portion of the key.

The reference implementation defines three signature schemes, although TUF
is not restricted to any particular signature scheme, key type, or
cryptographic library:

  : <dfn for="scheme">"rsassa-pss-sha256"</dfn>
  ::
    RSA Probabilistic signature scheme with appendix. The underlying hash
    function is SHA256. [https://tools.ietf.org/html/rfc3447#page-29
    ](https://tools.ietf.org/html/rfc3447#page-29)

  : <dfn for="scheme">"ed25519"</dfn>
  ::
    Elliptic curve digital signature algorithm based on Twisted Edwards curves.
    [https://ed25519.cr.yp.to/](https://ed25519.cr.yp.to/)

  : <dfn for="scheme">"ecdsa-sha2-nistp256"</dfn>
  ::
    Elliptic Curve Digital Signature Algorithm with NIST P-256 curve signing
    and SHA-256 hashing.
    [https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm
    ](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)

We define three keytypes below: <a for="keytype">"rsa"</a>, <a
for="keytype">"ed25519"</a>, and <a for="keytype">"ecdsa-sha2-nistp256"</a>, but adopters
can define and use any particular keytype, signing scheme, and cryptographic
library.

The <dfn for="keytype">"rsa"</dfn> format is:

<pre highlight="json">
{
  "keytype" : <a for="keytype">"rsa"</a>,
  "scheme" : <a for="scheme">"rsassa-pss-sha256"</a>,
  "keyval" : {
    "public" : <a for="keyval-rsa">PUBLIC</a>
  }
}
</pre>

  : <dfn for="keyval-rsa">PUBLIC</dfn>
  ::
    PEM format and a string.  All RSA keys MUST be at least 2048 bits.

The <dfn for="keytype">"ed25519"</dfn> format is:

<pre highlight="json">
{
  "keytype" : <a for="keytype">"ed25519"</a>,
  "scheme" : <a for="scheme">"ed25519"</a>,
  "keyval" : {
    "public" : <a for="keyval-ed25519">PUBLIC</a>
  }
}
</pre>

  : <dfn for="keyval-ed25519">PUBLIC</dfn>
  ::
    64-byte hex encoded string.

The <dfn for="keytype">"ecdsa-sha2-nistp256"</dfn> format is:

<pre highlight="json">
{
  "keytype" : <a for="keytype">"ecdsa-sha2-nistp256"</a>,
  "scheme" : <a for="scheme">"ecdsa-sha2-nistp256"</a>,
  "keyval" : {
    "public" : <a for="keyval-ecdsa">PUBLIC</a>
  }
}
</pre>

  : <dfn for="keyval-ecdsa">PUBLIC</dfn>
  ::
    PEM format and a string.

Metadata <dfn>date-time</dfn> follows the ISO 8601 standard.  The expected
format of the combined date and time string is "YYYY-MM-DDTHH:MM:SSZ".  Time is
always in UTC, and the "Z" time zone designator is attached to indicate a
zero UTC offset.  An example <a>date-time</a> string is "1985-10-21T01:21:00Z".


## File formats: root.json ## {#file-formats-root}

The <dfn>root.json</dfn> file is signed by the root role's keys.  It indicates
which keys are authorized for all top-level roles, including the root
role itself.  Revocation and replacement of top-level role keys, including
for the root role, is done by changing the keys listed for the roles in
this file.

The "signed" portion of <a>root.json</a> is as follows:

<pre highlight="json">
{
  "_type" : "root",
  "spec_version" : <a>SPEC_VERSION</a>,
  "consistent_snapshot": <a>CONSISTENT_SNAPSHOT</a>,
  "version" : <a for="role">VERSION</a>,
  "expires" : <a>EXPIRES</a>,
  "keys" : {
    <a for="root">KEYID</a> : <a>KEY</a>,
    ...
  },
  "roles" : {
    <a for="root">ROLE</a> : {
      "keyids" : [
        <a for="root">KEYID</a>,
        ...
      ] ,
      "threshold" : <a>THRESHOLD</a>
    },
    ...
  }
}
</pre>

  : <dfn>SPEC_VERSION</dfn>
  ::
    A string that contains the version number of the TUF
    specification.  Its format follows the [Semantic Versioning 2.0.0
    (semver)](https://semver.org/spec/v2.0.0.html) specification. Metadata is
    written according to version "spec_version" of the specification, and
    clients MUST verify that "spec_version" matches the expected version number.
    Adopters are free to determine what is considered a match (e.g., the version
    number exactly, or perhaps only the major version number (major.minor.fix).

  : <dfn>CONSISTENT_SNAPSHOT</dfn>
  ::
    An OPTIONAL boolean indicating whether the repository supports
    consistent snapshots. This field is OPTIONAL for backwards compatibility with
    old metadata. New implementations SHOULD include it. Section
    [[#consistent-snapshots]] goes into more detail on the consequences of
    enabling this setting on a repository.

  : <dfn for="role">VERSION</dfn>
  ::
    An integer that is greater than 0.  Clients MUST NOT replace a
    metadata file with a version number less than the one currently trusted.

  : <dfn>EXPIRES</dfn>
  ::
    A <a>date-time</a> string indicating when metadata should be considered
    expired and no longer trusted by clients.  Clients MUST NOT trust an
    expired file.

  : <dfn for="root">ROLE</dfn>
  ::
    One of "root", "snapshot", "targets", "timestamp", or "mirrors".
    A role for each of "root", "snapshot", "timestamp", and "targets" MUST be
    specified in the roles object. The role of "mirror" is OPTIONAL.  If not
    specified, the mirror list will not need to be signed if mirror lists are
    being used.

  : <dfn for="root">KEYID</dfn>
  ::
    A <a for="role">KEYID</a>, which MUST be correct for the specified KEY.
    Clients MUST calculate each <a for="role">KEYID</a> to verify this is
    correct for the associated key.  Clients MUST ensure that for any
    <a for="role">KEYID</a> represented in this key list and in other files,
    only one unique key has that <a for="role">KEYID</a>.

  : <dfn>THRESHOLD</dfn>
  ::
    An integer number of keys of that role whose signatures are required in
    order to consider a file as being properly signed by that role.

<div class='example' id='example-root.json'>
A <a>root.json</a> example file:

<pre highlight="json">
{
  "signatures": [
    {
      "keyid": "cb3fbd83df4ba2471a736b065650878280964a98843ec13b457a99b2a21cc3b4",
      "sig": "a312b9c3cb4a1b693e8ebac5ee1ca9cc01f2661c14391917dcb111517f72370809
              f32c890c6b801e30158ac4efe0d4d87317223077784c7a378834249d048306"
    }
  ],
  "signed": {
    "_type": "root",
    "spec_version": "1.0.0",
    "consistent_snapshot": false,
    "expires": "2030-01-01T00:00:00Z",
    "keys": {
      "1bf1c6e3cdd3d3a8420b19199e27511999850f4b376c4547b2f32fba7e80fca3": {
        "keytype": "ed25519",
        "scheme": "ed25519",
        "keyval": {
          "public": "72378e5bc588793e58f81c8533da64a2e8f1565c1fcc7f253496394ffc52542c"
        }
      },
      "135c2f50e57ff11e744d234a62cebad8c38daf399604a7655661cc9199c69164": {
        "keytype": "ed25519",
        "scheme": "ed25519",
        "keyval": {
          "public": "68ead6e54a43f8f36f9717b10669d1ef0ebb38cee6b05317669341309f1069cb"
        }
      },
      "cb3fbd83df4ba2471a736b065650878280964a98843ec13b457a99b2a21cc3b4": {
        "keytype": "ed25519",
        "scheme": "ed25519",
        "keyval": {
          "public": "66dd78c5c2a78abc6fc6b267ff1a8017ba0e8bfc853dd97af351949bba021275"
        }
      },
      "66676daa73bdfb4804b56070c8927ae491e2a6c2314f05b854dea94de8ff6bfc": {
        "keytype": "ed25519",
        "scheme": "ed25519",
        "keyval": {
          "public": "01c61f8dc7d77fcef973f4267927541e355e8ceda757e2c402818dad850f856e"
        }
      }
    },
    "roles": {
      "root": {
        "keyids": [
          "cb3fbd83df4ba2471a736b065650878280964a98843ec13b457a99b2a21cc3b4"
        ],
        "threshold": 1
      },
      "snapshot": {
        "keyids": [
          "66676daa73bdfb4804b56070c8927ae491e2a6c2314f05b854dea94de8ff6bfc"
        ],
        "threshold": 1
      },
      "targets": {
        "keyids": [
          "135c2f50e57ff11e744d234a62cebad8c38daf399604a7655661cc9199c69164"
        ],
        "threshold": 1
      },
      "timestamp": {
        "keyids": [
          "1bf1c6e3cdd3d3a8420b19199e27511999850f4b376c4547b2f32fba7e80fca3"
        ],
        "threshold": 1
      }
    },
    "version": 1
  }
}
</pre>
</div>

## File formats: snapshot.json ## {#file-formats-snapshot}

The <dfn>snapshot.json</dfn> file is signed by the snapshot role. It MUST list the
version numbers of the top-level targets metadata and all delegated targets
metadata. It MAY also list their lengths and file hashes.

The "signed" portion of <a>snapshot.json</a> is as follows:

<pre highlight="json">
{
  "_type" : "snapshot",
  "spec_version" : <a>SPEC_VERSION</a>,
  "version" : <a for="role">VERSION</a>,
  "expires" : <a>EXPIRES</a>,
  "meta" : <a>METAFILES</a>
}
</pre>

<a>SPEC_VERSION</a>, <a for="role">VERSION</a> and <a>EXPIRES</a> are the same
as is described for the <a>root.json</a> file.

<dfn>METAFILES</dfn> is an object whose format is the following:

<pre highlight="json">
{
  <a for="snapshot">METAPATH</a> : {
    "version" : <a for="metapath">VERSION</a>,
    ("length" : <a for="metapath">LENGTH</a>,)
    ("hashes" : <a for="metapath">HASHES</a>)
  },
  ...
}
</pre>

  : <dfn for="snapshot">METAPATH</dfn>
  ::
    A string giving the file path of the metadata on the repository relative to
    the metadata base URL.  For <a>snapshot.json</a>, these are top-level targets
    metadata and delegated targets metadata.

  : <dfn for="metapath">VERSION</dfn>
  ::
    An integer version number as shown in the metadata file at
    <a for="snapshot">METAPATH</a>.

  : <dfn for="metapath">LENGTH</dfn>
  ::
    An integer length in bytes of the metadata file at
    <a for="snapshot">METAPATH</a>. It is OPTIONAL and can be omitted to reduce
    the snapshot metadata file size.  In that case the client MUST use a custom
    download limit for the listed metadata.

  : <dfn for="metapath">HASHES</dfn>
  ::
    A dictionary that specifies one or more hashes of the metadata
    file at <a for="snapshot">METAPATH</a>, with the cryptographic hash
    function as key and the value as <dfn>HASH</dfn>, the hexdigest of the
    cryptographic function computed on the metadata file at
    <a for="snapshot">METAPATH</a>.  For example: `{ "sha256": HASH, ... }`.
    <a for="metapath">HASHES</a> is OPTIONAL and can be omitted to reduce the
    snapshot metadata file size.  In that case the repository MUST guarantee
    that <a for="metapath">VERSION</a> alone unambiguously identifies
    the metadata at <a for="snapshot">METAPATH</a>.

<div class="example" id="example-snapshot.json">
A <a>snapshot.json</a> example file:

<pre highlight="json">
{
  "signatures": [
    {
      "keyid": "66676daa73bdfb4804b56070c8927ae491e2a6c2314f05b854dea94de8ff6bfc",
      "sig": "f7f03b13e3f4a78a23561419fc0dd741a637e49ee671251be9f8f3fceedfc112e4
              4ee3aaff2278fad9164ab039118d4dc53f22f94900dae9a147aa4d35dcfc0f"
    }
  ],
  "signed": {
    "_type": "snapshot",
    "spec_version": "1.0.0",
    "expires": "2030-01-01T00:00:00Z",
    "meta": {
      "targets.json": {
        "version": 1
      },
      "project1.json": {
        "version": 1,
        "hashes": {
          "sha256": "f592d072e1193688a686267e8e10d7257b4ebfcf28133350dae88362d82a0c8a"
        }
      },
      "project2.json": {
        "version": 1,
        "length": 604,
        "hashes": {
          "sha256": "1f812e378264c3085bb69ec5f6663ed21e5882bbece3c3f8a0e8479f205ffb91"
        }
      }
    },
    "version": 1
  }
}
</pre>
</div>

## File formats: targets.json and delegated target roles ## {#file-formats-targets}

The "signed" portion of <dfn>targets.json</dfn> is as follows:

<pre highlight="json">
{
  "_type" : "targets",
  "spec_version" : <a>SPEC_VERSION</a>,
  "version" : <a for="role">VERSION</a>,
  "expires" : <a>EXPIRES</a>,
  "targets" : <a>TARGETS</a>,
  ("delegations" : <a>DELEGATIONS</a>)
}
</pre>

<a>SPEC_VERSION</a>, <a for="role">VERSION</a> and <a>EXPIRES</a> are the same
as is described for the <a>root.json</a> file.

<dfn for="targets-obj">TARGETS</dfn> is an object whose format is the following:

<pre highlight="json">
{
  <a>TARGETPATH</a> : {
      "length" : <a for="targets-obj">LENGTH</a>,
      "hashes" : <a for="targets-obj">HASHES</a>,
      ("custom" : <a>CUSTOM</a>) }
  , ...
}
</pre>

  : <a for="targets-obj">TARGETS</a>
  ::
    Each key of the <a for="targets-obj">TARGETS</a> object is a <a>TARGETPATH</a>.

  : <dfn>TARGETPATH</dfn>
  ::
    A string giving the path to a file that is relative to a mirror's base URL
    of targets.  To avoid surprising behavior when resolving paths, it is
    RECOMMENDED that a <a>TARGETPATH</a> uses the forward slash (/) as directory
    separator and does not start with a directory separator. The recommendation
    for <a>TARGETPATH</a> aligns with the ["path-relative-URL string"
    definition](https://url.spec.whatwg.org/#path-relative-url-string) in the
    WHATWG URL specification.

    It is allowed to have a <a>TARGETS</a> object with no <a>TARGETPATH</a>
    elements.  This can be used to indicate that no target files are available.

  : <dfn for="targets-obj">LENGTH</dfn>
  ::
    An integer length in bytes of the target file at <a>TARGETPATH</a>.

  : <dfn for="targets-obj">HASHES</dfn>
  ::
    A dictionary that specifies one or more hashes of the target file at
    <a>TARGETPATH</a>, with a string describing the cryptographic hash function
    as key and <a>HASH</a> as defined for <a>METAFILES</a>.  For example:
    `{ "sha256": HASH, ... }`.

  : <dfn>CUSTOM</a>
  ::
    An object.  If defined, the elements and values of the <a>CUSTOM</a> object
    will be made available to the client application.  The format of the
    <a>CUSTOM</a> object is opaque to the framework, which only needs to know
    that the "custom" attribute maps to an object.  The <a>CUSTOM</a> object
    may include version numbers, dependencies, requirements, or any other data
    that the application wants to include to describe the file at
    <a>TARGETPATH</a>.  The application may use this information to guide
    download decisions.

<dfn>DELEGATIONS</dfn> is an OPTIONAL object and if defined it has the following
format:

<pre highlight="json">
{
  "keys" : {
      <a for="role">KEYID</a> : <a>KEY</a>,
      ...
  },
  "roles" : [
    {
      "name": <a>ROLENAME</a>,
      "keyids" : [ <a for="role">KEYID</a>, ... ] ,
      "threshold" : <a>THRESHOLD</a>,
      (<a>"path_hash_prefixes"</a> : [ <a>HEX_DIGEST</a>, ... ] |
      <a for="delegation-role">"paths"</a> : [ <a>PATHPATTERN</a>, ... ]),
      "terminating": <a>TERMINATING</a>,
    },
    ...
  ]
}
</pre>

  <a for="root">KEYID</a> and <a>KEY</a> are the same as is described for the
  <a>root.json</a> file.

  : <dfn>ROLENAME</dfn>
  ::
    A string giving the name of the delegated role.  For example, "projects".
    The rolename MUST be unique in the delegations object: multiple roles with
    the same rolename are not allowed within a <a>DELEGATIONS</a>.

  : <dfn>TERMINATING</dfn>
  ::
    A boolean indicating whether subsequent delegations should be considered
    if a matching target is not found in this delegation.

    As explained in the [Diplomat paper
    ](https://theupdateframework.io/papers/protect-community-repositories-nsdi2016.pdf),
    terminating delegations instruct the client not to consider future trust
    statements that match this delegation's pattern, which stops the delegation
    processing once this delegation (and its descendants) have been processed.
    A terminating delegation for a package causes any further statements about a
    package that are not made by the delegated party or its descendants to be
    ignored.

The <a>"path_hash_prefixes"</a> and <a for="delegation-role">"paths"</a>
attributes are OPTIONAL, if used, exactly one of them should be set.

  : <dfn>"path_hash_prefixes"</dfn>
  ::
    A list of <dfn>HEX_DIGEST</dfn>s used to succinctly describe a set of target
    paths. Specifically, each HEX_DIGEST in <a>"path_hash_prefixes"</a>
    describes a set of target paths; therefore, <a>"path_hash_prefixes"</a> is
    the union over each prefix of its set of target paths.  The target paths
    must meet this condition: each target path, when hashed with the SHA-256
    hash function to produce a 64-byte hexadecimal digest
    (HEX_DIGEST), must share the same prefix as one of the prefixes
    in <a>"path_hash_prefixes"</a>.  This is useful to split a large number of
    targets into separate bins identified by consistent hashing.

  : <dfn for="delegation-role">"paths"</dfn>
  ::
    A list of strings, where each string is a <a>PATHPATTERN</a> describing a
    path that the delegated role is trusted to provide.  Clients MUST check that
    a target is in one of the trusted paths of all roles in a delegation chain,
    not just in a trusted path of the role that describes the target file.

    <dfn>PATHPATTERN</dfn> supports the Unix shell pattern matching convention
    for paths ([glob](https://man7.org/linux/man-pages/man7/glob.7.html)bing
    pathnames). Its format may either indicate a path to a single file, or to
    multiple files with the use of shell-style wildcards (`*` or `?`).
    To avoid surprising behavior when matching targets with <a>PATHPATTERN</a>,
    it is RECOMMENDED that <a>PATHPATTERN</a> uses the forward slash (`/`) as
    directory separator and does not start with a directory separator, as is
    also recommended for <a>TARGETPATH</a>. A path separator in a path SHOULD
    NOT be matched by a wildcard in the <a>PATHPATTERN</a>.

    Some example <a>PATHPATTERN</a>s and expected matches:
    * a <a>PATHPATTERN</a> of `"targets/*.tgz"` would match file paths
      `"targets/foo.tgz"` and `"targets/bar.tgz"`, but not `"targets/foo.txt"`.
    * a <a>PATHPATTERN</a> of `"foo-version-?.tgz"` matches
      `"foo-version-2.tgz"` and `"foo-version-a.tgz"`, but not
      `"foo-version-alpha.tgz"`.
    * a <a>PATHPATTERN</a> of `"*.tgz"` would match `"foo.tgz"` and `"bar.tgz"`,
      but not `"targets/foo.tgz"`
    * a <a>PATHPATTERN</a> of `"foo.tgz"` would match only `"foo.tgz"`


Prioritized delegations allow clients to resolve conflicts between delegated
roles that share responsibility for overlapping target paths.  To resolve
conflicts, clients must consider metadata in order of appearance of delegations;
we treat the order of delegations such that the first delegation is trusted
over the second one, the second delegation is trusted more than the third
one, and so on. Likewise, the metadata of the first delegation will override that
of the second delegation, the metadata of the second delegation will override
that of the third one, etc. In order to accommodate prioritized
delegations, the "roles" key in the <a>DELEGATIONS</a> object above points to an array
of delegated roles, rather than to a hash table.

The metadata files for delegated target roles has the same format as the
top-level <a>targets.json</a> metadata file.

<div class="example" id="example-targets.json">
A <a>targets.json</a> example file:

<pre highlight="json">
{
  "signatures": [
    {
      "keyid": "135c2f50e57ff11e744d234a62cebad8c38daf399604a7655661cc9199c69164",
      "sig": "e9fd40008fba263758a3ff1dc59f93e42a4910a282749af915fbbea1401178e5a0
              12090c228f06db1deb75ad8ddd7e40635ac51d4b04301fce0fd720074e0209"
    }
  ],
  "signed": {
    "_type": "targets",
    "spec_version": "1.0.0",
    "delegations": {
      "keys": {
        "f761033eb880143c52358d941d987ca5577675090e2215e856ba0099bc0ce4f6": {
          "keytype": "ed25519",
          "scheme": "ed25519",
          "keyval": {
            "public": "b6e40fb71a6041212a3d84331336ecaa1f48a0c523f80ccc762a034c727606fa"
          }
        }
      },
      "roles": [
        {
          "keyids": [
            "f761033eb880143c52358d941d987ca5577675090e2215e856ba0099bc0ce4f6"
          ],
          "name": "project",
          "paths": [
            "project/file3.txt"
          ],
          "threshold": 1
        }
      ]
    },
    "expires": "2030-01-01T00:00:00Z",
    "targets": {
      "file1.txt": {
        "hashes": {
          "sha256": "65b8c67f51c993d898250f40aa57a317d854900b3a04895464313e48785440da"
        },
        "length": 31
      },
      "dir/file2.txt": {
        "hashes": {
          "sha256": "452ce8308500d83ef44248d8e6062359211992fd837ea9e370e561efb1a4ca99"
        },
        "length": 39
      }
    },
    "version": 1
  }
}
</pre>
</div>

## File formats: timestamp.json ## {#file-formats-timestamp}

The <dfn>timestamp.json</dfn> file is signed by the timestamp role.  It indicates the latest
version of the snapshot metadata and is frequently re-signed to limit the
amount of time a client can be kept unaware of interference with obtaining
updates.

Timestamp files will potentially be downloaded very frequently.  Unnecessary
information in them will be avoided.

The "signed" portion of <a>timestamp.json</a> is as follows:

<pre highlight="json">
{
  "_type" : "timestamp",
  "spec_version" : <a>SPEC_VERSION</a>,
  "version" : <a for="role">VERSION</a>,
  "expires" : <a>EXPIRES</a>,
  "meta" : <a>METAFILES</a>
}
</pre>

<a>SPEC_VERSION</a>, <a for="role">VERSION</a> and <a>EXPIRES</a> are the same as is described for the <a>root.json</a> file.

<a>METAFILES</a> is the same as described for the <a>snapshot.json</a> file.  In the case
of the <a>timestamp.json</a> file, this MUST only include a description of the
<a>snapshot.json</a> file.

<div class="example" id="example-timestamp.json">
A signed <a>timestamp.json</a> example file:
<pre highlight="json">
{
  "signatures": [
    {
      "keyid": "1bf1c6e3cdd3d3a8420b19199e27511999850f4b376c4547b2f32fba7e80fca3",
      "sig": "90d2a06c7a6c2a6a93a9f5771eb2e5ce0c93dd580bebc2080d10894623cfd6eaed
              f4df84891d5aa37ace3ae3736a698e082e12c300dfe5aee92ea33a8f461f02"
    }
  ],
  "signed": {
    "_type": "timestamp",
    "spec_version": "1.0.0",
    "expires": "2030-01-01T00:00:00Z",
    "meta": {
      "snapshot.json": {
        "hashes": {
          "sha256": "c14aeb4ac9f4a8fc0d83d12482b9197452f6adf3eb710e3b1e2b79e8d14cb681"
        },
        "length": 1007,
        "version": 1
      }
    },
    "version": 1
  }
}
</pre>
</div>

## File formats: mirrors.json ## {#file-formats-mirrors}

The <dfn>mirrors.json</dfn> file is signed by the mirrors role.  It indicates which
mirrors are active and believed to be mirroring specific parts of the
repository.

The "signed" portion of <a>mirrors.json</a> is as follows:

<pre highlight="json">
{
  "_type" : "mirrors",
  "spec_version" : <a>SPEC_VERSION</a>,
  "version" : <a for="role">VERSION</a>,
  "expires" : <a>EXPIRES</a>,
  "mirrors" : [
    { "urlbase" : <a>URLBASE</a>,
      "metapath" : <a for="mirrors">METAPATH</a>,
      "targetspath" : <a>TARGETSPATH</a>,
      "metacontent" : [ <a>PATHPATTERN</a> ... ] ,
      "targetscontent" : [ <a>PATHPATTERN</a> ... ] ,
      ("custom" : { ... }) }
    , ... ]
}
</pre>

<a>SPEC_VERSION</a>, <a for="role">VERSION</a> and <a>EXPIRES</a> are the same
as is described for the <a>root.json</a> file.

  : <dfn>URLBASE</dfn>
  ::
    A string giving the URL of the mirror.

  : <dfn for="mirrors">METAPATH</dfn>
  ::
    A string giving the location from which to retrieve metadata files.
    <a for="mirrors">METAPATH</a> will be a relative path to <a>URLBASE</a>.

  : <dfn>TARGETSPATH</a>
  ::
    A string giving the location from which to retrieve target files.
    <a>TARGETSPATH</a> will be a relative path to <a>URLBASE</a>.

The lists of <a>PATHPATTERN</a> for "metacontent" and "targetscontent" describe the
metadata files and target files available from the mirror.

The order of the list of mirrors is important.  For any file to be
downloaded, whether it is a metadata file or a target file, the framework on
the client will give priority to the mirrors that are listed first.  That is,
the first mirror in the list whose "metacontent" or "targetscontent" include
a path that indicate the desired file can be found there will the first
mirror that will be used to download that file.  Successive mirrors with
matching paths will only be tried if downloading from earlier mirrors fails.
This behavior can be modified by the client code that uses the framework to,
for example, randomly select from the listed mirrors.

# Detailed client workflow # {#detailed-client-workflow}

Note: If a step in the following workflow does not succeed (e.g., the update
is aborted because a new metadata file was not signed), the client should
still be able to update again in the future. Errors raised during the update
process should not leave clients in an unrecoverable state.

## Record fixed update start time ## {#fix-time}

Record the time at which the update began as the fixed update start time.
Time is fixed at the beginning of the update workflow to allow
an application using TUF to effectively pause time, in order to ensure that
metadata which has a valid expiration time at the beginning of an update
does not fail an expiration check later in the update workflow.

## Load trusted root metadata ## {#load-trusted-root}

Load the trusted root metadata file.  We assume that a good,
trusted copy of this file was shipped with the package manager or software
updater using an out-of-band process.  Note that the expiration of the
trusted root metadata file does not matter, because we will attempt to update
it in the next step.

## Update the root role ## {#update-root}

1. Since it may now be signed using entirely different keys, the client MUST
  somehow be able to establish a trusted line of continuity to the latest set
  of keys (see [[#key-management-and-migration]]).  To do so, the client MUST
  download intermediate root metadata files, until the latest available one is
  reached.

2. Let N denote the version number of the trusted root metadata
  file.

3. **Try downloading version N+1 of the root metadata file**, up to
  some W number of bytes (because the size is unknown). The value for W is set
  by the authors of the application using TUF. For example, W may be tens of
  kilobytes. The filename used to download the root metadata file is of the
  fixed form VERSION_NUMBER.FILENAME.EXT (e.g., 42.root.json). If this file is
  not available, or we have downloaded more than Y number of root metadata
  files (because the exact number is as yet unknown), then go to step 5.3.10.
  The value for Y is set by the authors of the application using TUF. For
  example, Y may be 2^10.

4. **Check for an arbitrary software attack.** Version N+1 of the root
  metadata file MUST have been signed by: (1) a threshold of keys specified in
  the trusted root metadata file (version N), and (2) a threshold of keys
  specified in the new root metadata file being validated (version N+1).  If
  version N+1 is not signed as required, discard it, abort the update cycle,
  and report the signature failure.

5. **Check for a rollback attack.** The version number of the new root
  metadata (version N+1) MUST be exactly the version in the trusted root
  metadata (version N) incremented by one, that is precisely N+1.
  If the version of the new root metadata file is not N+1, discard it,
  abort the update cycle, and report the rollback attack.

6. Note that the expiration of the new (intermediate) root metadata
  file does not matter yet, because we will check for it in step 5.3.10.

7. **Set the trusted root metadata file** to the new root metadata
  file.

8. **Persist root metadata.** The client MUST write the file to
  non-volatile storage as FILENAME.EXT (e.g. root.json).

9. Repeat steps 5.3.2 to 5.3.9

10. **Check for a freeze attack.** The expiration timestamp in the
  trusted root metadata file MUST be higher than the fixed update start time.
  If the trusted root metadata file has expired, abort the update cycle,
  report the potential freeze attack.

11. **If the timestamp and / or snapshot keys have been rotated, then delete the
  trusted timestamp and snapshot metadata files.** This is done
  in order to recover from fast-forward attacks after the repository has been
  compromised and recovered. A *fast-forward attack* happens when attackers
  arbitrarily increase the version numbers of: (1) the timestamp metadata, (2)
  the snapshot metadata, and / or (3) the targets, or a delegated targets,
  metadata file in the snapshot metadata. Please see [the Mercury
  paper](https://theupdateframework.io/papers/prevention-rollback-attacks-atc2017.pdf)
  for more details.

12. **Set whether consistent snapshots are used as per the trusted**
    root metadata file (see [[#file-formats-root]]).

## Update the timestamp role ## {#update-timestamp}

1. **Download the timestamp metadata file**, up to X number of bytes
  (because the size is unknown). The value for X is set by the authors of the
  application using TUF. For example, X may be tens of kilobytes. The filename
  used to download the timestamp metadata file is of the fixed form FILENAME.EXT
  (e.g., timestamp.json).

2. **Check for an arbitrary software attack.** The new timestamp
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file. If the new timestamp metadata file is not
  properly signed, discard it, abort the update cycle, and report the signature
  failure.

3. **Check for a rollback attack.**

  1. The version number of the trusted timestamp metadata file, if
    any, MUST be less than the version number of the new timestamp
    metadata file. If the new timestamp metadata version is less than the trusted
    timestamp metadata version, discard it, abort the update cycle, and
    report the potential rollback attack. In case they are equal, discard the new
    timestamp metadata and abort the update cycle. This is normal and it
    shouldn't raise any error. The reason for aborting the update process is that
    there shouldn't be any changes in the content of this, or any other metadata
    files too, considering it has the same version as the already trusted one.

  2. The version number of the snapshot metadata file in the
    trusted timestamp metadata file, if any, MUST be less than or equal to its
    version number in the new timestamp metadata file. If not, discard the new
    timestamp metadata file, abort the update cycle, and report the failure.

4. **Check for a freeze attack.** The expiration timestamp in the
  new timestamp metadata file MUST be higher than the fixed update start time.
  If so, the new timestamp metadata file becomes the trusted timestamp
  metadata file.  If the new timestamp metadata file has expired, discard it,
  abort the update cycle, and report the potential freeze attack.

5. **Persist timestamp metadata**. The client MUST write the file
  to non-volatile storage as FILENAME.EXT (e.g. timestamp.json).

## Update the snapshot role ## {#update-snapshot}

1. **Download snapshot metadata file**, up to either the number of bytes
  specified in the timestamp metadata file, or some Y number of bytes. The value
  for Y is set by the authors of the application using TUF. For example, Y may be
  tens of kilobytes. If consistent snapshots are not used (see
  Section [[#consistent-snapshots]]), then the filename used to download the
  snapshot metadata file is of the fixed form FILENAME.EXT (e.g.,
  snapshot.json).  Otherwise, the filename is of the form
  VERSION_NUMBER.FILENAME.EXT (e.g., 42.snapshot.json), where VERSION_NUMBER is
  the version number of the snapshot metadata file listed in the timestamp
  metadata file.

2. **Check against timestamp role's snapshot hash**. The hashes
  of the new snapshot metadata file MUST match the hashes, if any, listed in
  the trusted timestamp metadata.  This is done, in part, to prevent a
  mix-and-match attack by man-in-the-middle attackers. It is safe to check the
  hashes before the signatures, because the hashes come from the timestamp
  role, which we have already verified in the previous step; it is also a quick
  way to reject bad metadata. If the hashes do not match, discard the
  new snapshot metadata, abort the update cycle, and report the failure.

3. **Check for an arbitrary software attack**. The new snapshot
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file.  If the new snapshot metadata file is not signed
  as required, discard it, abort the update cycle, and report the signature
  failure.

4. **Check against timestamp role's snapshot version**. The version
  number of the new snapshot metadata file MUST match the version number listed
  in the trusted timestamp metadata.  If the versions do not match, discard the
  new snapshot metadata, abort the update cycle, and report the failure.

5. **Check for a rollback attack**. The version number of the targets
  metadata file, and all delegated targets metadata files, if any, in the
  trusted snapshot metadata file, if any, MUST be less than or equal to its
  version number in the new snapshot metadata file. Furthermore, any targets
  metadata filename that was listed in the trusted snapshot metadata file, if
  any, MUST continue to be listed in the new snapshot metadata file.  If any of
  these conditions are not met, discard the new snapshot metadata file, abort
  the update cycle, and report the failure.

6. **Check for a freeze attack**. The expiration timestamp in the
  new snapshot metadata file MUST be higher than the fixed update start time.
  If so, the new snapshot metadata file becomes the trusted snapshot metadata
  file.  If the new snapshot metadata file is expired, discard it, abort the
  update cycle, and report the potential freeze attack.


7. **Persist snapshot metadata**. The client MUST write the file to
  non-volatile storage as FILENAME.EXT (e.g. snapshot.json).

## Update the targets role ## {#update-targets}

1. **Download the top-level targets metadata file**, up to either the
  number of bytes specified in the snapshot metadata file, or some Z number of
  bytes. The value for Z is set by the authors of the application using TUF. For
  example, Z may be tens of kilobytes.  If consistent snapshots are not used (see
  [[#consistent-snapshots]]), then the filename used to download the targets
  metadata file is of the fixed form FILENAME.EXT (e.g., targets.json).
  Otherwise, the filename is of the form VERSION_NUMBER.FILENAME.EXT (e.g.,
  42.targets.json), where VERSION_NUMBER is the version number of the targets
  metadata file listed in the snapshot metadata file.

2. **Check against snapshot role's targets hash**. The hashes
  of the new targets metadata file MUST match the hashes, if any, listed in the
  trusted snapshot metadata.  This is done, in part, to prevent a mix-and-match
  attack by man-in-the-middle attackers. It is safe to check the hashes before
  the signatures, because the hashes come from the snapshot role, which we have
  already verified in the previous step; it is also a quick way to reject bad
  metadata. If the new targets metadata file does not match, discard the new
  target metadata, abort the update cycle, and report the failure.

3. **Check for an arbitrary software attack**. The new targets
  metadata file MUST have been signed by a threshold of keys specified in the
  trusted root metadata file.  If the new targets metadata file is not signed
  as required, discard it, abort the update cycle, and report the failure.

4. **Check against snapshot role's targets version**. The version
  number of the new targets metadata file MUST match the version number listed
  in the trusted snapshot metadata.  If the versions do not match, discard it,
  abort the update cycle, and report the failure.

5. **Check for a freeze attack**. The expiration timestamp in the
  new targets metadata file MUST be higher than the fixed update start time.
  If so, the new targets metadata file becomes the trusted targets metadata
  file.  If the new targets metadata file is expired, discard it, abort the
  update cycle, and report the potential freeze attack.

6. **Persist targets metadata**. The client MUST write the file to
  non-volatile storage as FILENAME.EXT (e.g. targets.json).

7. **Perform a pre-order depth-first search for metadata about the
  desired target, beginning with the top-level targets role.** Note: If
  any metadata requested in steps 5.6.7.1 - 5.6.7.2 cannot be downloaded nor
  validated, end the search and report that the target cannot be found.

  1. If this role has been visited before, then skip this role
     (so that cycles in the delegation graph are avoided).  Otherwise, if an
     application-specific maximum number of roles have been visited, then go to
     step [[#fetch-target]] (so that attackers cannot cause the client to waste excessive
     bandwidth or time).  Otherwise, if this role contains metadata about the
     desired target, then go to step [[#fetch-target]].

  2. Otherwise, recursively search the list of delegations in
     order of appearance.

    1. If the current delegation is a terminating delegation,
       then jump to step [[#fetch-target]].

    2. Otherwise, if the current delegation is a
       non-terminating delegation, continue processing the next delegation, if
       any. Stop the search, and jump to step [[#fetch-target]] as soon as a delegation
       returns a result.

## Fetch target ## {#fetch-target}

1. **Verify the desired target against its targets metadata**.

2. If there is no targets metadata about this target, abort the
    update cycle and report that there is no such target.

3. Otherwise, download the target (up to the number of bytes
   specified in the targets metadata), and verify that its hashes match the
   targets metadata. (We download up to this number of bytes, because in some
   cases, the exact number is unknown. This may happen, for example, if an
   external program is used to compute the root hash of a tree of targets files,
   and this program does not provide the total size of all of these files.) If
   consistent snapshots are not used (see [[#consistent-snapshots]]), then the
   filename used to download the target file is of the fixed form FILENAME.EXT
   (e.g., foobar.tar.gz).  Otherwise, the filename is of the form
   HASH.FILENAME.EXT (e.g.,
   c14aeb4ac9f4a8fc0d83d12482b9197452f6adf3eb710e3b1e2b79e8d14cb681.foobar.tar.gz),
   where HASH is one of the hashes of the targets file listed in the targets
   metadata file found earlier in step [[#update-targets]].  In either
   case, the client MUST write the file to non-volatile storage as FILENAME.EXT.

# Repository operations # {#repository-operations}

See [https://theupdateframework.io/](https://theupdateframework.io/) for
discussion of recommended usage in various situations.

## Key management and migration ## {#key-management-and-migration}

All keys, except those for the timestamp and mirrors roles, should be
stored securely offline (e.g. encrypted and on a separate machine, in
special-purpose hardware, etc.).  This document does not prescribe how keys
should be encrypted and stored, and so it is left to implementers of
this document to decide how best to secure them.

To replace a compromised root key or any other top-level role key, the root
role signs a new root.json file that lists the updated trusted keys for the
role.  When replacing root keys, an application will sign the new root.json
file with both the new and old root keys. Any time such a change is
required, the root.json file is versioned and accessible by version number,
e.g., 3.root.json.

Clients that have outdated root keys can update to the latest set of trusted
root keys, by incrementally downloading all intermediate root metadata
files, and verifying that each current version of the root metadata is
signed by a threshold of keys specified by its immediate predecessor as well
as a threshold of keys specified by itself.
For example, if there is a 1.root.json that has threshold 2 and a
2.root.json that has threshold 3, 2.root.json MUST be signed by at least 2
keys defined in 1.root.json and at least 3 keys defined in 2.root.json. The
client starts the root key update process with the latest version of root
metadata available on the client, and stops when no version N+1 (where N is
the latest trusted version) of the root metadata is available from the
repository. This ensures that an outdated client can always correctly
re-trace the chain of trust across multiple root key updates, even if the
latest set of root keys on the client dates back multiple root metadata
versions. See step [[#update-root]]  of the client application workflow for more details.

Note that an attacker, who controls the repository, can launch freeze
attacks by withholding new root metadata. The attacker does not need to
compromise root keys to do so. However, these freeze attacks are limited by
the expiration time of the latest root metadata available to the client.

To replace a delegated developer key, the role that delegated to that key
just replaces that key with another in the signed metadata where the
delegation is done.

## Consistent snapshots ## {#consistent-snapshots}

So far, we have considered a TUF repository that is relatively static (in
terms of how often metadata and target files are updated). The problem is
that if the repository (which may be a community repository such as PyPI,
RubyGems, CPAN, or SourceForge) is volatile, in the sense that the
repository is continually producing new TUF metadata as well as its targets,
then should clients read metadata while the same metadata is being written
to, they would effectively see denial-of-service attacks.  Therefore, the
repository needs to be careful about how it writes metadata and targets. The
high-level idea of the solution is that each snapshot will be contained in a
so-called consistent snapshot. If a client is reading from one consistent
snapshot, then the repository is free to write another consistent snapshot
without interrupting that client.

### Writing consistent snapshots ### {#writing-consistent-snapshots}

We now explain how a repository should write metadata and targets to
produce self-contained consistent snapshots.

Simply put, every metadata file MUST be named as such: if the
file had the original name of FILENAME.EXT, then it MUST be written to
non-volatile storage as VERSION_NUMBER.FILENAME.EXT, where VERSION_NUMBER
is the integer version number listed in the metadata file.

On the other hand, consistent target files MUST be written to
non-volatile storage as HASH.FILENAME.EXT.  This means that if the
referrer metadata lists N cryptographic hashes of the referred file, then
there MUST be N identical copies of the referred file, where each file will
be distinguished only by the value of the digest in its filename. The
modified filename need not include the name of the cryptographic hash
function used to produce the digest because, on a read, the choice of
function follows from the selection of a digest (which includes the name of
the cryptographic function) from all digests in the referred file.

Timestamp metadata (timestamp.EXT) MUST be written to non-volatile storage
without a version prefix whenever it is updated. This is required because
timestamp metadata is the only metadata file that may be requested without known
version numbers.  It is OPTIONAL for an implementation to write an identical copy
of timestamp.EXT to the respective VERSION_NUMBER.timestamp.EXT for
record-keeping purposes.

Most importantly, metadata file formats SHALL NOT be updated to refer to the
names of metadata or target files with their consistent snapshot prefix
included. In other words, if a metadata file A refers to another metadata file B
as FILENAME.EXT, then the filename listed in the metadata MUST remain as
FILENAME.EXT and not VERSION_NUMBER.FILENAME.EXT. This rule is in place so that
metadata signed by roles with offline keys will not be forced to sign for the
metadata file whenever it is updated. In the next subsection, we will see how
clients will reproduce the name of the intended file.

Finally, when consistent snapshots are written by the repository the root
metadata MUST write the boolean <a>CONSISTENT_SNAPSHOT</a> attribute at the root
level of its keys of attributes set to the true value. If consistent snapshots
are not written by the repository, then the attribute MAY either be left
unspecified or be set to the false value.

Regardless of whether consistent snapshots are ever used or not, all
released versions of root metadata files MUST always be provided
so that outdated clients can update to the latest available root.


### Reading consistent snapshots ### {#reading-consistent-snapshots}

See [[#detailed-client-workflow]] for more details.

## Adding and updating targets ## {#adding-updating-targets}

The following subsections describe how to update metadata on the repository
when adding targets to the repository, or updating existing targets.

### Update targets metadata ### {#update-targets-metadata}

1. Add the new (or update an existing) <a>TARGETS</a> object in the relevant
   targets metadata (either the top-level targets metadata, or a delegated
   targets metadata).
2. Increment the <a for="role">VERSION</a> number in the updated targets
   metadata.
3. Sign the updated targets metadata with at least a <a>THRESHOLD</a> of keys
   for the associated targets role (either the top-level targets role, or a
   delegated targets role).
4. Write the updated targets metadata, ensuring the targets metadata filename is
   prefixed with the <a for="role">VERSION</a> number if consistent snapshots
   are enabled for the repository.

### Update snapshot metadata ### {#update-snapshot-metadata}

1. Update the <a for="metapath">VERSION</a> number and, when in use,
   <a for="metapath">LENGTH</a> and <a for="metapath">HASHES</a> for any targets
   metadata modified during [[#update-targets-metadata]] within the
   <a>METAFILES</a> object of the snapshot metadata.
2. Increment the <a for="role">VERSION</a> number of the snapshot metadata.
3. Sign the snapshot metadata with at least a <a>THRESHOLD</a> of keys for the
   snapshot role.
4. Write the updated snapshot metadata, ensuring the snapshot metadata filename
   is prefixed with the <a for="role">VERSION</a> number if consistent
   snapshots are enabled for the repository.

### Update timestamp metadata ### {#update-timestamp-metadata}

1. Update the <a for="metapath">VERSION</a> and, when in use, the
   <a for="metapath">LENGTH</a> and <a for="metapath">HASHES</a> for the
   snapshot metadata within the <a>METAFILES</a> object of the timestamp
   metadata.
2. Increment the <a for="role">VERSION</a> number of the timestamp metadata.
3. Sign the timestamp metadata with at least a <a>THRESHOLD</a> of keys for the
   timestamp role.
4. Write the updated timestamp metadata, ensuring the timestamp metadata
   filename is prefixed with the <a for="role">VERSION</a> number if consistent
   snapshots are enabled for the repository.

# Future directions and open questions # {#future-directions-and-open-questions}

## Support for bogus clocks ## {#support-for-bogus-clocks}

The framework may need to offer an application-enablable "no, my clock is
*supposed* to be wrong" mode, since others have noticed that many users seem
to have incorrect clocks.
