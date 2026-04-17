# Explicit Contracts Guide

Use this guide when deciding whether a boundary in the repository needs a DTO,
`Protocol`, or other explicit contract.

This is a durable decision aid, not the canonical governance source. For binding
rules, use `.specify/memory/constitution.md`.

## Goal

The repository should avoid hidden coupling between modules, layers, and
runtimes.

An explicit contract is useful when a caller should not need historical
knowledge of payload shape, magic keys, or implicit object behavior to use a
boundary safely.

## When `dict` Is Fine

`dict` is acceptable when it is clearly:

- final serialization at an HTTP or presentation boundary
- temporary parsing of external JSON before conversion to a typed shape
- a private cache or internal infrastructure detail
- a local implementation detail that does not cross a reusable module boundary

Good examples:

- presenter converting DTO to JSON payload
- transport code reading raw response JSON before mapping it
- private internal cache stats used only inside one adapter

## When A Contract Should Be Explicit

Use a DTO, named result object, or `Protocol` when:

- data crosses reusable module boundaries
- multiple layers depend on the same shape
- bot and desktop both rely on the result
- the boundary uses magic keys like `payload["x"]`
- a service exposes status or results to other modules
- an object is consumed by behavior rather than just passed through

Good candidates:

- use case input/output objects
- status objects shared across modules
- integration responses after transport parsing
- runtime interfaces consumed through behavior rather than concrete class access

## DTO Vs `Protocol`

Prefer a DTO when:

- you are passing structured data
- the shape is mostly values
- serialization or documentation matters
- immutability or named fields improve readability

Prefer a `Protocol` when:

- the boundary is behavioral
- the caller depends on methods, not raw data
- multiple implementations can satisfy the same role
- you want explicit duck typing without concrete coupling

## Keep Dynamic Details At The Edge

Some APIs are naturally dynamic and do not need full formalization in the core
of the system.

Usually acceptable at the edge:

- Tkinter widgets and toolkit object handles
- concrete library objects such as engine/session/client instances
- transport-layer raw payloads before mapping

The important rule is not "ban dynamic objects". The rule is: do not let those
dynamic details become the semantic contract between reusable modules.

## Smells That Indicate An Implicit Contract

- code depends on undocumented key names
- a result shape is re-created in more than one module
- callers need comments or tribal knowledge to know what fields exist
- changing a key name breaks distant modules silently
- tests assert on ad-hoc payload shape instead of a named result type

## Practical Rule Of Thumb

If another contributor could ask "what exactly does this function return?" and
the answer is "it depends on these keys being present", that boundary probably
deserves an explicit contract.

If the answer is "it returns this named result" or "it accepts anything that
implements this behavior", the boundary is usually in a healthier place.
