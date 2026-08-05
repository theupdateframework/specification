# Scope of The Update Framework (TUF) Specification Working Group

## 1. Objective
The objective of The Update Framework (TUF) Working Group is to define, standardize, and maintain a framework for securing software update systems, specifically mitigating known attacks against software repositories (e.g., rollback, freeze, mix-and-match, and malicious repository compromises).

## 2. In Scope
The Working Group's standard-setting activities are strictly limited to the following areas required to achieve client-server interoperability:

* **Metadata Data Models and Schemas:** The structure, syntax, semantics, and serialization formats (e.g., canonical JSON) of the core TUF metadata roles (Root, Targets, Snapshot, Timestamp) and any standardized extension roles.
* **Client Verification Workflow:** The step-by-step state machine, algorithmic logic, and failure conditions a client must execute to securely fetch, validate, and process repository metadata and target files.
* **Delegation and Trust Boundaries:** Mechanisms for threshold signing, cryptographic key delegation, repository segmentation, and key revocation within the metadata structure.
* **Cryptographic Representation:** The specifications for how cryptographic hashes, signatures, and key material are represented, encoded, and bound to the metadata roles.
* **Threat Mitigation Definitions:** Explicit descriptions of the specific software update threat models the framework addresses, serving as the basis for the protocol's security properties.

## 3. Out of Scope
To prevent unintentional intellectual property encumbrance, the following areas are explicitly excluded from the Working Group's scope:

* **Payload Semantics:** The definition, structure, execution, or content of the target files distributed by the framework (e.g., binaries, containers, source code, or other supply chain metadata).
* **Transport Protocols:** The definition or standardization of network transport layers or delivery mechanisms (e.g., HTTP, gRPC, IPFS) used to transmit metadata or targets.
* **Cryptographic Primitives:** The invention, modification, or primary standardization of underlying cryptographic algorithms (e.g., Ed25519, SHA-256). The specification relies entirely on existing cryptographic standards.
* **Server-Side Architecture:** The design, implementation, and operational architecture of backend repository servers, metadata generation tools, or key management infrastructure at the implementation level. The specification governs the artifacts produced by the server and consumed by clients at an algorithmic level and does not mandate an exact means of producing the information.
* 
Any changes of Scope are not retroactive.
