<pre class=metadata>
Status: DREAM
Shortname: tuf
Abstract: todo
Group: tuf
Title: The Update Framework Specification
Editor: foo
Indent: 2
Boilerplate: copyright no
</pre>

Last modified: **30 September 2020**

Version: **1.0.9**

We strive to make the specification easy to implement, so if you come across
any inconsistencies or experience any difficulty, do let us know by sending an
email to our [mailing
list](https://groups.google.com/forum/?fromgroups#!forum/theupdateframework),
or by reporting an issue in the [specification
repo](https://github.com/theupdateframework/specification/issues).


# Introduction

## Scope

   This document describes a framework for securing software update systems.

   The keywords "MUST," "MUST NOT," "REQUIRED," "SHALL," "SHALL NOT," "SHOULD,"
   "SHOULD NOT," "RECOMMENDED," "MAY," and "OPTIONAL" in this document are to be
   interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

## Motivation

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

## History and credit

   Work on TUF began in late 2009.  The core ideas are based off of previous
   work done by Justin Cappos and Justin Samuel that [identified security flaws
   in all popular Linux package managers](https://theupdateframework.io/papers/attacks-on-package-managers-ccs2008.pdf).
   More information and current versions of this document can be found at
   https://theupdateframework.io/

   The [Global Environment for Network Innovations](https://www.geni.net/) (GENI)
   and the [National Science Foundation](https://www.nsf.gov/) (NSF) have
   provided support for the development of TUF.

   TUF's reference implementation is based on prior work on
   [Thandy](https://www.torproject.org/), the application
   updater for Tor. Its design and this spec
   also came from ideas jointly developed in discussion with Thandy's authors.
   The Thandy spec can be found at
   https://gitweb.torproject.org/thandy.git/tree/specs/thandy-spec.txt

   Whereas Thandy is an application updater for an individual software project,
   TUF aims to provide a way to secure any software update system. We're very
   grateful to the Tor Project and the Thandy developers for the early discussion
   that led to the ideas in Thandy and TUF. Thandy is the hard
   work of Nick Mathewson, Sebastian Hahn, Roger Dingledine, Martin Peck, and
   others.

## Non-goals

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

## Goals

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

### Goals for implementation

      + The client side of the framework must be straightforward to implement in any
        programming language and for any platform with the requisite networking and
        crypto support.

      +  The process by which developers push updates to the repository must be
         simple.

      + The framework must be secure to use in environments that lack support for
        SSL (TLS).  This does not exclude the optional use of SSL when available,
        but the framework will be designed without it.

### Goals to protect against specific attacks

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

### Goals for PKI

      * Software update systems using the framework's client code interface should
        never have to directly manage keys.

      * All keys must be easily and safely revocable.  Trusting new keys for a role
        must be easy.

      * For roles where trust delegation is meaningful, a role should be able to
        delegate full or limited trust to another role.

      * The root of trust must not rely on external PKI.  That is, no authority will
        be derived from keys outside of the framework.

### TUF Augmentation Proposal support

      * This version (1.0.0) of the specification adheres to the following TAPS:

        - [TAP 6](https://github.com/theupdateframework/taps/blob/master/tap6.md):
            Include specification version in metadata
        - [TAP 9](https://github.com/theupdateframework/taps/blob/master/tap9.md):
            Mandatory Metadata signing schemes
        - [Tap 10](https://github.com/theupdateframework/taps/blob/master/tap10.md):
            Remove native support for compressed metadata

        Implementations compliant with this version (1.0.0) of the specification
        must also comply with the TAPs mentioned above.

# System overview

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

       Polling:
            Periodically, the software update system using the framework
            instructs the framework to check each repository for updates.  If
            the framework reports to the application code that there are
            updates, the application code determines whether it wants to
            download the updated target files.  Only target files that are
            trusted (referenced by properly signed and timely metadata) are
            made available by the framework.

       Fetching:
            For each file that the application wants, it asks the framework to
            download the file.  The framework downloads the file and performs
            security checks to ensure that the downloaded file is exactly what
            is expected according to the signed metadata.  The application code
            is not given access to the file until the security checks have been
            completed.  The application asks the framework to copy the
            downloaded file to a location specified by the application.  At
            this point, the application has securely obtained the target file
            and can do with it whatever it wishes.

## Roles and PKI

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

### Root Role

      + The root role delegates trust to specific keys trusted for all other
        top-level roles used in the system.

      + The client-side of the framework MUST ship with trusted root keys for each
        configured repository.

      + The root role's private keys MUST be kept very secure and thus should be
        kept offline.  If less than a threshold of Root keys are compromised, the
        repository should revoke trust on the compromised keys.  This can be
        accomplished with a normal rotation of root keys, covered in section 6.1
        (Key management and migration). If a threshold of root keys is compromised,
        the Root keys should be updated out-of-band, however, the threshold should
        be chosen so that this is extremely unlikely.  In the unfortunate event that
        a threshold of keys are compromised, it is safest to assume that attackers
        have installed malware and taken over affected machines.  For this reason,
        making it difficult for attackers to compromise all of the offline keys is
        important because safely recovering from it is nearly impossible.


### Targets role

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

### Snapshot role

      The snapshot role signs a metadata file that provides information about
      the latest version of all targets metadata on the repository
      (the top-level targets role and all delegated roles).  This information allows
      clients to know which metadata files have been updated and also prevents
      mix-and-match attacks.

### Timestamp role

      To prevent an adversary from replaying an out-of-date signed metadata file
      whose signature has not yet expired, an automated process periodically signs
      a timestamped statement containing the hash of the snapshot file.  Even
      though this timestamp key must be kept online, the risk posed to clients by
      the compromise of this key is minimal.

### Mirrors role

      Every repository has one or more mirrors from which files can be downloaded
      by clients.  A software update system using the framework may choose to
      hard-code the mirror information in their software or they may choose to use
      mirror metadata files that can optionally be signed by a mirrors role.

      The importance of using signed mirror lists depends on the application and
      the users of that application.  There is minimal risk to the application's
      security from being tricked into contacting the wrong mirrors.  This is
      because the framework has very little trust in repositories.

## Threat Model And Analysis

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

# The repository

   An application uses the framework to interact with one or more repositories.
   A repository is a conceptual source of target files of interest to the
   application.  Each repository has one or more mirrors which are the actual
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

## Repository layout

   The filesystem layout in the repository is used for two purposes:
     - To give mirrors an easy way to mirror only some of the repository.
     - To specify which parts of the repository a given role has authority
         to sign/provide.

### Target files

   The filenames and the directory structure of target files available from
   a repository are not specified by the framework.  The names of these files
   and directories are completely at the discretion of the application using
   the framework.

### Metadata files

   The filenames and directory structure of repository metadata are strictly
   defined.  All metadata filenames will have an extension (EXT) based on the
   metaformat, for example JSON metadata files would have an EXT of json.
   The following are the metadata files of top-level roles relative
   to the base URL of metadata available from a given repository mirror.

    /root.EXT

         Signed by the root keys; specifies trusted keys for the other
         top-level roles.

    /snapshot.EXT

         Signed by the snapshot role's keys.  Lists the version numbers of all
         target metadata files: the top-level targets.EXT and all delegated
         roles.

    /targets.EXT

         Signed by the target role's keys.  Lists hashes and sizes of target
         files. Specifies delegation information and trusted keys for delegated
         target roles.

    /timestamp.EXT

         Signed by the timestamp role's keys.  Lists hash(es), size, and version
         number of the snapshot file.  This is the first and potentially only
         file that needs to be downloaded when clients poll for the existence
         of updates.

    /mirrors.EXT (optional)

         Signed by the mirrors role's keys.  Lists information about available
         mirrors and the content available from each mirror.

#### Metadata files for targets delegation

   When the targets role delegates trust to other roles, each delegated role
   provides one signed metadata file.  As is the case with the directory
   structure of top-level metadata, the delegated files are relative to the
   base URL of metadata available from a given repository mirror.

   A delegated role file is located at:

    /DELEGATED_ROLE.EXT

   where DELEGATED_ROLE is the name of the delegated role that has been
   specified in targets.EXT.  If this role further delegates trust to a role
   named ANOTHER_ROLE, that role's signed metadata file is made available at:

    /ANOTHER_ROLE.EXT

   Delegated target roles are authorized by the keys listed in the directly
   delegating target role.

# Document formats

   All of the formats described below include the ability to add more
   attribute-value fields for backwards-compatible format changes.  If
   a backwards incompatible format change is needed, a new filename can
   be used.

## Metaformat

   Implementers of TUF may use any data format for metadata files as long as
   all fields in this specification are included and TUF clients are able to
   interpret them without ambiguity. Implementers should choose a data format
   that allows for canonicalization, or one that will decode data
   deterministically by default so that signatures can be accurately verified.
   The examples in this document use a subset of the JSON object format, with
   floating-point numbers omitted.  When calculating the digest of an
   object, we use the "canonical JSON" subdialect as described at
        http://wiki.laptop.org/go/Canonical_JSON

## File formats: general principles

   All signed metadata objects have the format:

       { "signed" : ROLE,
         "signatures" : [
            { "keyid" : KEYID,
              "sig" : SIGNATURE }
            , ... ]
       }

   where:

          ROLE is a dictionary whose "_type" field describes the role type.

          KEYID is the identifier of the key signing the ROLE dictionary.

          SIGNATURE is a hex-encoded signature of the canonical form of
          the metadata for ROLE.


   All keys have the format:

        { "keytype" : KEYTYPE,
          "scheme" : SCHEME,
          "keyval" : KEYVAL
        }

   where:

          KEYTYPE is a string denoting a public key signature system, such
          as RSA or ECDSA.

          SCHEME is a string denoting a corresponding signature scheme.  For
          example: "rsassa-pss-sha256" and "ecdsa-sha2-nistp256".

          KEYVAL is a dictionary containing the public portion of the key.

   The reference implementation defines three signature schemes, although TUF
   is not restricted to any particular signature scheme, key type, or
   cryptographic library:

       "rsassa-pss-sha256" : RSA Probabilistic signature scheme with appendix.
        The underlying hash function is SHA256.
        https://tools.ietf.org/html/rfc3447#page-29

       "ed25519" : Elliptic curve digital signature algorithm based on Twisted
        Edwards curves.
        https://ed25519.cr.yp.to/

        "ecdsa-sha2-nistp256" : Elliptic Curve Digital Signature Algorithm
         with NIST P-256 curve signing and SHA-256 hashing.
         https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm

   We define three keytypes below: 'rsa', 'ed25519', and 'ecdsa', but adopters
   can define and use any particular keytype, signing scheme, and cryptographic
   library.

   The 'rsa' format is:

        { "keytype" : "rsa",
          "scheme" : "rsassa-pss-sha256",
          "keyval" : {"public" : PUBLIC}
        }

   where PUBLIC is in PEM format and a string.  All RSA keys MUST be at least
   2048 bits.

   The 'ed25519' format is:

        { "keytype" : "ed25519",
          "scheme" : "ed25519",
          "keyval" : {"public" : PUBLIC}
        }

   where:

          PUBLIC is a 64-byte hex encoded string.

   The 'ecdsa' format is:

        { "keytype" : "ecdsa-sha2-nistp256",
          "scheme" : "ecdsa-sha2-nistp256",
          "keyval" : {"public" : PUBLIC}
        }

   where:

        PUBLIC is in PEM format and a string.

   The KEYID of a key is the hexdigest of the SHA-256 hash of the
   canonical form of the key.

   Metadata date-time data follows the ISO 8601 standard.  The expected format
   of the combined date and time string is "YYYY-MM-DDTHH:MM:SSZ".  Time is
   always in UTC, and the "Z" time zone designator is attached to indicate a
   zero UTC offset.  An example date-time string is "1985-10-21T01:21:00Z".


## File formats: root.json

   The root.json file is signed by the root role's keys.  It indicates
   which keys are authorized for all top-level roles, including the root
   role itself.  Revocation and replacement of top-level role keys, including
   for the root role, is done by changing the keys listed for the roles in
   this file.

   The "signed" portion of root.json is as follows:

       { "_type" : "root",
         "spec_version" : SPEC_VERSION,
         "consistent_snapshot": CONSISTENT_SNAPSHOT,
         "version" : VERSION,
         "expires" : EXPIRES,
         "keys" : {
             KEYID : KEY
             , ... },
         "roles" : {
             ROLE : {
               "keyids" : [ KEYID, ... ] ,
               "threshold" : THRESHOLD }
             , ... }
       }

   SPEC_VERSION is a string that contains the version number of the TUF
   specification. Its format follows the [Semantic Versioning 2.0.0
   (semver)](https://semver.org/spec/v2.0.0.html) specification. Metadata is
   written according to version "spec_version" of the specification, and
   clients MUST verify that "spec_version" matches the expected version number.
   Adopters are free to determine what is considered a match (e.g., the version
   number exactly, or perhaps only the major version number (major.minor.fix).

   CONSISTENT_SNAPSHOT is a boolean indicating whether the repository supports
   consistent snapshots.  Section 7 goes into more detail on the consequences
   of enabling this setting on a repository.

   VERSION is an integer that is greater than 0.  Clients MUST NOT replace a
   metadata file with a version number less than the one currently trusted.

   EXPIRES determines when metadata should be considered expired and no longer
   trusted by clients.  Clients MUST NOT trust an expired file.

   A ROLE is one of "root", "snapshot", "targets", "timestamp", or "mirrors".
   A role for each of "root", "snapshot", "timestamp", and "targets" MUST be
   specified in the key list. The role of "mirror" is OPTIONAL.  If not
   specified, the mirror list will not need to be signed if mirror lists are
   being used.

   The KEYID MUST be correct for the specified KEY.  Clients MUST calculate
   each KEYID to verify this is correct for the associated key.  Clients MUST
   ensure that for any KEYID represented in this key list and in other files,
   only one unique key has that KEYID.

   The THRESHOLD for a role is an integer of the number of keys of that role
   whose signatures are required in order to consider a file as being properly
   signed by that role.

   A root.json example file:

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

## File formats: snapshot.json

   The snapshot.json file is signed by the snapshot role. It MUST list the
   version numbers of the top-level targets metadata and all delegated targets
   metadata. It MAY also list their lengths and file hashes.

   The "signed" portion of snapshot.json is as follows:

       { "_type" : "snapshot",
         "spec_version" : SPEC_VERSION,
         "version" : VERSION,
         "expires" : EXPIRES,
         "meta" : METAFILES
       }

   SPEC_VERSION, VERSION and EXPIRES are the same as is described for the root.json file.

   METAFILES is an object whose format is the following:

       { METAPATH : {
             "version" : VERSION,
             ("length" : LENGTH, |
              "hashes" : HASHES) }
         , ...
       }

   METAPATH is the file path of the metadata on the repository relative to the
   metadata base URL. For snapshot.json, these are top-level targets metadata
   and delegated targets metadata.

   VERSION is the integer version number as shown in the metadata file at
   METAPATH.

   LENGTH is the integer length in bytes of the metadata file at METAPATH. It
   is OPTIONAL and can be omitted to reduce the snapshot metadata file size. In
   that case the client MUST use a custom download limit for the listed
   metadata.

   HASHES is a dictionary that specifies one or more hashes of the metadata
   file at METAPATH, including their cryptographic hash function. For example:
   { "sha256": HASH, ... }. HASHES is OPTIONAL and can be omitted to reduce
   the snapshot metadata file size.  In that case the repository MUST guarantee
   that VERSION alone unambiguously identifies the metadata at METAPATH.

   A snapshot.json example file:

       { "signatures": [
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

## File formats: targets.json and delegated target roles

   The "signed" portion of targets.json is as follows:

       { "_type" : "targets",
         "spec_version" : SPEC_VERSION,
         "version" : VERSION,
         "expires" : EXPIRES,
         "targets" : TARGETS,
         ("delegations" : DELEGATIONS)
       }

   SPEC_VERSION, VERSION and EXPIRES are the same as is described for the root.json file.

   TARGETS is an object whose format is the following:

       { TARGETPATH : {
             "length" : LENGTH,
             "hashes" : HASHES,
             ("custom" : { ... }) }
         , ...
       }

   Each key of the TARGETS object is a TARGETPATH.  A TARGETPATH is a path to
   a file that is relative to a mirror's base URL of targets. To avoid
   surprising behavior when resolving paths, it is RECOMMENDED that a
   TARGETPATH uses the forward slash (/) as directory separator and does not
   start with a directory separator. The recommendation for TARGETPATH aligns
   with the ["path-relative-URL string"
   definition](https://url.spec.whatwg.org/#path-relative-url-string) in the
   WHATWG URL specification.

   It is allowed to have a TARGETS object with no TARGETPATH elements.  This
   can be used to indicate that no target files are available.

   LENGTH is the integer length in bytes of the target file at TARGETPATH.

   HASHES is a dictionary that specifies one or more hashes, including the
   cryptographic hash function.  For example: { "sha256": HASH, ... }. HASH is
   the hexdigest of the cryptographic function computed on the target file.

   If defined, the elements and values of "custom" will be made available to the
   client application.  The information in "custom" is opaque to the framework
   and can include version numbers, dependencies, requirements, and any other
   data that the application wants to include to describe the file at
   TARGETPATH.  The application may use this information to guide download
   decisions.

   DELEGATIONS is an object whose format is the following:

       { "keys" : {
             KEYID : KEY,
             ... },
         "roles" : [{
             "name": ROLENAME,
             "keyids" : [ KEYID, ... ] ,
             "threshold" : THRESHOLD,
             ("path_hash_prefixes" : [ HEX_DIGEST, ... ] |
              "paths" : [ PATHPATTERN, ... ]),
             "terminating": TERMINATING,
         }, ... ]
       }

   "keys" lists the public keys to verify signatures of delegated targets roles.
   Revocation and replacement of delegated targets roles keys is done by
   changing the keys in this field in the delegating role's metadata.

   ROLENAME is the name of the delegated role.  For example,
   "projects".

   TERMINATING is a boolean indicating whether subsequent delegations should be
   considered.

   As explained in the [Diplomat
   paper](https://github.com/theupdateframework/tuf/blob/develop/docs/papers/protect-community-repositories-nsdi2016.pdf),
   terminating delegations instruct the client not to consider future trust
   statements that match the delegation's pattern, which stops the delegation
   processing once this delegation (and its descendants) have been processed.
   A terminating delegation for a package causes any further statements about a
   package that are not made by the delegated party or its descendants to be
   ignored.

   In order to discuss target paths, a role MUST specify only one of the
   "path_hash_prefixes" or "paths" attributes, each of which we discuss next.

   The "path_hash_prefixes" list is used to succinctly describe a set of target
   paths. Specifically, each HEX_DIGEST in "path_hash_prefixes" describes a set
   of target paths; therefore, "path_hash_prefixes" is the union over each
   prefix of its set of target paths. The target paths must meet this
   condition: each target path, when hashed with the SHA-256 hash function to
   produce a 64-byte hexadecimal digest (HEX_DIGEST), must share the same
   prefix as one of the prefixes in "path_hash_prefixes". This is useful to
   split a large number of targets into separate bins identified by consistent
   hashing.

   The "paths" list describes paths that the role is trusted to provide.
   Clients MUST check that a target is in one of the trusted paths of all roles
   in a delegation chain, not just in a trusted path of the role that describes
   the target file.  PATHPATTERN can include shell-style wildcards and supports
   the Unix filename pattern matching convention.  Its format may either
   indicate a path to a single file, or to multiple paths with the use of
   shell-style wildcards.  For example, the path pattern "targets/*.tgz" would
   match file paths "targets/foo.tgz" and "targets/bar.tgz", but not
   "targets/foo.txt".  Likewise, path pattern "foo-version-?.tgz" matches
   "foo-version-2.tgz" and "foo-version-a.tgz", but not "foo-version-alpha.tgz".
   To avoid surprising behavior when matching targets with PATHPATTERN, it is
   RECOMMENDED that PATHPATTERN uses the forward slash (/) as directory
   separator and does not start with a directory separator, akin to
   TARGETSPATH.


   Prioritized delegations allow clients to resolve conflicts between delegated
   roles that share responsibility for overlapping target paths.  To resolve
   conflicts, clients must consider metadata in order of appearance of delegations;
   we treat the order of delegations such that the first delegation is trusted
   over the second one, the second delegation is trusted more than the third
   one, and so on. Likewise, the metadata of the first delegation will override that
   of the second delegation, the metadata of the second delegation will override
   that of the third one, etc. In order to accommodate prioritized
   delegations, the "roles" key in the DELEGATIONS object above points to an array
   of delegated roles, rather than to a hash table.

   The metadata files for delegated target roles has the same format as the
   top-level targets.json metadata file.

   A targets.json example file:

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

## File formats: timestamp.json

   The timestamp file is signed by a timestamp key.  It indicates the latest
   version of the snapshot metadata and is frequently re-signed to limit the
   amount of time a client can be kept unaware of interference with obtaining
   updates.

   Timestamp files will potentially be downloaded very frequently.  Unnecessary
   information in them will be avoided.

   The "signed" portion of timestamp.json is as follows:

       { "_type" : "timestamp",
         "spec_version" : SPEC_VERSION,
         "version" : VERSION,
         "expires" : EXPIRES,
         "meta" : METAFILES
       }

   SPEC_VERSION, VERSION and EXPIRES are the same as is described for the root.json file.

   METAFILES is the same as described for the snapshot.json file.  In the case
   of the timestamp.json file, this MUST only include a description of the
   snapshot.json file.

   A signed timestamp.json example file:

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

## File formats: mirrors.json

   The mirrors.json file is signed by the mirrors role.  It indicates which
   mirrors are active and believed to be mirroring specific parts of the
   repository.

   The "signed" portion of mirrors.json is as follows:


      { "_type" : "mirrors",
       "spec_version" : SPEC_VERSION,
       "version" : VERSION,
       "expires" : EXPIRES,
       "mirrors" : [
          { "urlbase" : URLBASE,
            "metapath" : METAPATH,
            "targetspath" : TARGETSPATH,
            "metacontent" : [ PATHPATTERN ... ] ,
            "targetscontent" : [ PATHPATTERN ... ] ,
            ("custom" : { ... }) }
          , ... ]
      }

   URLBASE is the URL of the mirror which METAPATH and TARGETSPATH are relative
   to.  All metadata files will be retrieved from METAPATH and all target files
   will be retrieved from TARGETSPATH.

   The lists of PATHPATTERN for "metacontent" and "targetscontent" describe the
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

# Detailed Workflows

## The client application

  Note: If a step in the following workflow does not succeed (e.g., the update
  is aborted because a new metadata file was not signed), the client should
  still be able to update again in the future. Errors raised during the update
  process should not leave clients in an unrecoverable state.

## Load the trusted root metadata file.

We assume that a good,
  trusted copy of this file was shipped with the package manager or software
  updater using an out-of-band process.  Note that the expiration of the
  trusted root metadata file does not matter, because we will attempt to update
  it in the next step.

## Update the root metadata file.

Since it may now be signed using
  entirely different keys, the client MUST somehow be able to establish a
  trusted line of continuity to the latest set of keys (see Section 6.1). To do
  so, the client MUST download intermediate root metadata files, until the
  latest available one is reached. Therefore, it MUST temporarily turn on
  consistent snapshots in order to download _versioned_ root metadata files as
  described next.

### Let N denote the version number of the trusted root metadata
    file.

### Try downloading version N+1 of the root metadata file

, up to
    some W number of bytes (because the size is unknown). The value for W is set
    by the authors of the application using TUF. For example, W may be tens of
    kilobytes. The filename used to download the root metadata file is of the
    fixed form VERSION_NUMBER.FILENAME.EXT (e.g., 42.root.json). If this file is
    not available, or we have downloaded more than Y number of root metadata
    files (because the exact number is as yet unknown), then go to step 5.1.9.
    The value for Y is set by the authors of the application using TUF. For
    example, Y may be 2^10.

### Check for an arbitrary software attack

Version N+1 of the root
    metadata file MUST have been signed by: (1) a threshold of keys specified in
    the trusted root metadata file (version N), and (2) a threshold of keys
    specified in the new root metadata file being validated (version N+1).  If
    version N+1 is not signed as required, discard it, abort the update cycle,
    and report the signature failure.  On the next update cycle, begin at step
    5.0 and version N of the root metadata file.

### Check for a rollback attack.**

The version number of the trusted
    root metadata file (version N) MUST be less than or equal to the version
    number of the new root metadata file (version N+1). Effectively, this means
    checking that the version number signed in the new root metadata file is
    indeed N+1.  If the version of the new root metadata file is less than the
    trusted metadata file, discard it, abort the update cycle, and report the
    rollback attack.  On the next update cycle, begin at step 5.0 and version N
    of the root metadata file.

### Note that the expiration of the new (intermediate) root metadata
    file does not matter yet, because we will check for it in step 5.1.9.

### Set the trusted root metadata file

to the new root metadata
    file.

### Persist root metadata

The client MUST write the file to
    non-volatile storage as FILENAME.EXT (e.g. root.json).

### Repeat steps 5.1.1 to 5.1.8

### Check for a freeze attack

The latest known time MUST be
    lower than the expiration timestamp in the trusted root metadata file
    (version N).  If the trusted root metadata file has expired, abort the update
    cycle, report the potential freeze attack.  On the next update cycle, begin
    at step 5.0 and version N of the root metadata file.

### If the timestamp and / or snapshot keys have been rotated,

    then delete the trusted timestamp and snapshot metadata files.** This is done
    in order to recover from fast-forward attacks after the repository has been
    compromised and recovered. A _fast-forward attack_ happens when attackers
    arbitrarily increase the version numbers of: (1) the timestamp metadata, (2)
    the snapshot metadata, and / or (3) the targets, or a delegated targets,
    metadata file in the snapshot metadata. Please see [the Mercury
    paper](https://ssl.engineering.nyu.edu/papers/kuppusamy-mercury-usenix-2017.pdf)
    for more details.

 ###  **Set whether consistent snapshots are used as per the trusted
    root metadata file** (see Section 4.3).

## **Download the timestamp metadata file**, up to X number of bytes
  (because the size is unknown). The value for X is set by the authors of the
  application using TUF. For example, X may be tens of kilobytes. The filename
  used to download the timestamp metadata file is of the fixed form FILENAME.EXT
  (e.g., timestamp.json).

### Check for an arbitrary software attack

The new timestamp
    metadata file MUST have been signed by a threshold of keys specified in the
    trusted root metadata file.  If the new timestamp metadata file is not
    properly signed, discard it, abort the update cycle, and report the signature
    failure.

### Check for a rollback attack

#### The version number of the trusted timestamp metadata file, if
      any, MUST be less than or equal to the version number of the new timestamp
      metadata file.  If the new timestamp metadata file is older than the
      trusted timestamp metadata file, discard it, abort the update cycle, and
      report the potential rollback attack.

#### The version number of the snapshot metadata file in the
      trusted timestamp metadata file, if any, MUST be less than or equal to its
      version number in the new timestamp metadata file.  If not, discard the new
      timestamp metadata file, abort the update cycle, and report the failure.

### Check for a freeze attack

The latest known time MUST be
    lower than the expiration timestamp in the new timestamp metadata file.  If
    so, the new timestamp metadata file becomes the trusted timestamp metadata
    file.  If the new timestamp metadata file has expired, discard it, abort the
    update cycle, and report the potential freeze attack.

### Persist timestamp metadata

The client MUST write the file
    to non-volatile storage as FILENAME.EXT (e.g. timestamp.json).

## **Download snapshot metadata file**, up to either the number of bytes
  specified in the timestamp metadata file, or some Y number of bytes. The value
  for Y is set by the authors of the application using TUF. For example, Y may be
  tens of kilobytes. If consistent snapshots are not used (see
  Section 7), then the filename used to download the snapshot metadata file is of
  the fixed form FILENAME.EXT (e.g., snapshot.json).  Otherwise, the filename is
  of the form VERSION_NUMBER.FILENAME.EXT (e.g., 42.snapshot.json), where
  VERSION_NUMBER is the version number of the snapshot metadata file listed in
  the timestamp metadata file.

### Check against timestamp metadata

The hashes and version
    number of the new snapshot metadata file MUST match the hashes, if any, and
    version number listed in the trusted timestamp metadata.  If hashes and
    version do not match, discard the new snapshot metadata, abort the update
    cycle, and report the failure.

### Check for an arbitrary software attack

The new snapshot
    metadata file MUST have been signed by a threshold of keys specified in the
    trusted root metadata file.  If the new snapshot metadata file is not signed
    as required, discard it, abort the update cycle, and report the signature
    failure.

### Check for a rollback attack

The version number of the targets
    metadata file, and all delegated targets metadata files, if any, in the
    trusted snapshot metadata file, if any, MUST be less than or equal to its
    version number in the new snapshot metadata file. Furthermore, any targets
    metadata filename that was listed in the trusted snapshot metadata file, if
    any, MUST continue to be listed in the new snapshot metadata file.  If any of
    these conditions are not met, discard the new snapshot metadata file, abort
    the update cycle, and report the failure.

### Check for a freeze attack

The latest known time MUST be
    lower than the expiration timestamp in the new snapshot metadata file.  If
    so, the new snapshot metadata file becomes the trusted snapshot metadata
    file. If the new snapshot metadata file is expired, discard it, abort the
    update cycle, and report the potential freeze attack.

### Persist snapshot metadata

The client MUST write the file to
    non-volatile storage as FILENAME.EXT (e.g. snapshot.json).

## **Download the top-level targets metadata file**, up to either the
  number of bytes specified in the snapshot metadata file, or some Z number of
  bytes. The value for Z is set by the authors of the application using TUF. For
  example, Z may be tens of kilobytes.  If consistent snapshots are not used (see
  Section 7), then the filename used to download the targets metadata file is of
  the fixed form FILENAME.EXT (e.g., targets.json).  Otherwise, the filename is
  of the form VERSION_NUMBER.FILENAME.EXT (e.g., 42.targets.json), where
  VERSION_NUMBER is the version number of the targets metadata file listed in the
  snapshot metadata file.

### Check against snapshot metadata

The hashes and version
    number of the new targets metadata file MUST match the hashes, if any, and
    version number listed in the trusted snapshot metadata.  This is done, in
    part, to prevent a mix-and-match attack by man-in-the-middle attackers.  If
    the new targets metadata file does not match, discard it, abort the update
    cycle, and report the failure.

### **Check for an arbitrary software attack

The new targets
    metadata file MUST have been signed by a threshold of keys specified in the
    trusted root metadata file.  If the new targets metadata file is not signed
    as required, discard it, abort the update cycle, and report the failure.

### **Check for a freeze attack

The latest known time MUST be
    lower than the expiration timestamp in the new targets metadata file.  If so,
    the new targets metadata file becomes the trusted targets metadata file.  If
    the new targets metadata file is expired, discard it, abort the update cycle,
    and report the potential freeze attack.

### Persist targets metadata

The client MUST write the file to
    non-volatile storage as FILENAME.EXT (e.g. targets.json).

### Perform a pre-order depth-first search for metadata about the desired target, beginning with the top-level targets role

Note: If
    any metadata requested in steps 5.4.5.1 - 5.4.5.2 cannot be downloaded nor
    validated, end the search and report that the target cannot be found.

#### If this role has been visited before, then skip this role
      (so that cycles in the delegation graph are avoided).  Otherwise, if an
      application-specific maximum number of roles have been visited, then go to
      step 5.5 (so that attackers cannot cause the client to waste excessive
      bandwidth or time).  Otherwise, if this role contains metadata about the
      desired target, then go to step 5.5.

#### Otherwise, recursively search the list of delegations in
      order of appearance.

##### If the current delegation is a multi-role delegation,
        recursively visit each role, and check that each has signed exactly the
        same non-custom metadata (i.e., length and hashes) about the target (or
        the lack of any such metadata).

##### If the current delegation is a terminating delegation,
        then jump to step 5.5.

##### Otherwise, if the current delegation is a
        non-terminating delegation, continue processing the next delegation, if
        any. Stop the search, and jump to step 5.5 as soon as a delegation
        returns a result.

## **Verify the desired target against its targets metadata**.

### If there is no targets metadata about this target, abort the
    update cycle and report that there is no such target.

### Otherwise, download the target (up to the number of bytes
    specified in the targets metadata), and verify that its hashes match the
    targets metadata. (We download up to this number of bytes, because in some
    cases, the exact number is unknown. This may happen, for example, if an
    external program is used to compute the root hash of a tree of targets files,
    and this program does not provide the total size of all of these files.) If
    consistent snapshots are not used (see Section 7), then the filename used to
    download the target file is of the fixed form FILENAME.EXT (e.g.,
    foobar.tar.gz).  Otherwise, the filename is of the form HASH.FILENAME.EXT
    (e.g.,
    c14aeb4ac9f4a8fc0d83d12482b9197452f6adf3eb710e3b1e2b79e8d14cb681.foobar.tar.gz),
    where HASH is one of the hashes of the targets file listed in the targets
    metadata file found earlier in step 4.  In either case, the client MUST write
    the file to non-volatile storage as FILENAME.EXT.

# Usage

   See https://theupdateframework.io/ for discussion of recommended usage
   in various situations.

## Key management and migration

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
   versions. See step 5.1 of the client application workflow for more details.

   Note that an attacker, who controls the repository, can launch freeze
   attacks by withholding new root metadata. The attacker does not need to
   compromise root keys to do so. However, these freeze attacks are limited by
   the expiration time of the latest root metadata available to the client.

   To replace a delegated developer key, the role that delegated to that key
   just replaces that key with another in the signed metadata where the
   delegation is done.

# Consistent Snapshots

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

## Writing consistent snapshots

    We now explain how a repository should write metadata and targets to
    produce self-contained consistent snapshots.

    Simply put, TUF should write every metadata file as such: if the
    file had the original name of filename.ext, then it should be written to
    non-volatile storage as version_number.filename.ext, where version_number
    is an integer.

    On the other hand, consistent target files should be written to
    non-volatile storage as digest.filename.ext.  This means that if the
    referrer metadata lists N cryptographic hashes of the referred file, then
    there must be N identical copies of the referred file, where each file will
    be distinguished only by the value of the digest in its filename. The
    modified filename need not include the name of the cryptographic hash
    function used to produce the digest because, on a read, the choice of
    function follows from the selection of a digest (which includes the name of
    the cryptographic function) from all digests in the referred file.

    Additionally, the timestamp metadata (timestamp.json) should also be
    written to non-volatile storage whenever it is updated. It is OPTIONAL for
    an implementation to write identical copies at
    version_number.timestamp.json for record-keeping purposes, because a
    cryptographic hash of the timestamp metadata is usually not known in
    advance. The same step applies to the root metadata (root.json), although
    an implementation must write both root.json and version_number.root.json
    because it is possible to download root metadata both with and without
    known version numbers. These steps are required because these are the only
    metadata files that may be requested without known version numbers.

    Most importantly, no metadata file format must be updated to refer to the
    names of metadata or target files with their version numbers included. In
    other words, if a metadata file A refers to another metadata file B as
    filename.ext, then the filename must remain as filename.ext and not
    version_number.filename.ext. This rule is in place so that metadata signed
    by roles with offline keys will not be forced to sign for the metadata file
    whenever it is updated. In the next subsection, we will see how clients
    will reproduce the name of the intended file.

    Finally, the root metadata should write the Boolean "consistent_snapshot"
    attribute at the root level of its keys of attributes. If consistent
    snapshots are not written by the repository, then the attribute may either
    be left unspecified or be set to the False value.  Otherwise, it must be
    set to the True value.

    Regardless of whether consistent snapshots are ever used or not, all
    released versions of root metadata files should always be provided
    so that outdated clients can update to the latest available root.


## Reading consistent snapshots

    See Section 5.1 for more details.

# Future directions and open questions

## Support for bogus clocks.

   The framework may need to offer an application-enablable "no, my clock is
   _supposed_ to be wrong" mode, since others have noticed that many users seem
   to have incorrect clocks.
