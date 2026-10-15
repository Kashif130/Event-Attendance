# EventAttendance v0.2 -- design decisions

## Starting point and review findings

v0.1 checked attendance on an organizer page by requiring the attendee's wallet address and an event
code in the page's main content. Reviewing it turned up these gaps:

1. **Anyone could create an event under someone else's domain.** Nothing proved the creator controlled
   the confirmation-page prefix. This is the most serious gap, because it made every badge depend on a
   page the creator did not own.
2. **Event codes could repeat under one prefix.** Two events could share a page and a code.
3. **Hex-address validation accepted non-ASCII digits.** `str.isdigit()` returns True for characters such
   as Arabic-Indic zero, so a malformed "address" passed. Fixed with an explicit ASCII hex set.
4. **No way to issue badges outside the page flow.** Offline check-ins, QR scans, speakers and
   corrections had no route.
5. **No staff model.** Only the organizer could manage attendees.
6. **No third-party verification call** and no EIP-5192-style lock query.
7. **No paginated indexes.** Event and wallet badge lists could not be read without scanning storage.
8. **No multi-event credential.** Galxe-style series and Sismo-style groups had no counterpart.

## Research basis

- **POAP** uses organizer-issued claim codes and delegated, signed minting. This version covers delegated
  minting through `organizer_mint` for staff. Claim codes are left out (see Trade-offs).
- **EIP-5192 (minimal soulbound NFT)** defines a `locked(tokenId)` view and treats non-transferability as
  an interface property. `is_locked` follows that pattern. Badges have no transfer function.
- **EAS (Ethereum Attestation Service)** schemas for event attendance use fields such as event name,
  location, check-in time, and revocable attestations. Badges carry the event location, issue time, source
  and revocation reason, and `get_badge_metadata` exposes them in a shape a verifier can read.
- **Galxe and Sismo** use credentials that combine several attestations and are earned by completing a
  set. Series credentials follow that model, with a limit of 10 events per series.

## Decisions

- **Verify the domain before accepting claims.** The organizer must publish a per-event token in the
  prefix page's main content, checked by consensus. Verification is deterministic in spirit: the page
  either contains the token or does not, and no LLM is involved. Comments are excluded, so a visitor
  cannot verify someone else's event by posting the token in a comment.
- **Event codes are unique per prefix**, enforced at creation.
- **Staff is a separate role.** Staff can manage attendees, mint, and resolve appeals. Verification,
  ownership, delegation, and extending the claim window stay with the organizer. Moderators keep their
  existing powers over pausing, closing, cancelling and revoking.
- **Organizer minting is marked as its own source.** Verifiers can tell a page-verified badge from a
  staff-issued one, and an appeal approval from a direct issue.
- **Indexes are written at issue time**, so reads never scan storage. The index for a badge is set when it
  is issued and is never removed, because badges are not deleted, only revoked.
- **Series credentials are permissionless to create** and do no harm: they only pay out a badge to a
  wallet that already holds every listed event's badge. Completion ignores revoked badges, and an issued
  series badge is not revoked retroactively.
- **Display names are checked and discarded**, so no personal data reaches contract state.
- **No money.** Escrow and reward flows would bring back the reservation mechanics from the quest
  contract without serving this use case.

## Trade-offs and residual risk

- **Claim codes are not implemented.** Single-use codes are the most common POAP claim method, and this
  is the largest feature gap. Implementing them safely would require hashing the codes on chain, or keeping
  them secret off chain and verifying them through the organizer's page. Neither is available here, so
  staff minting covers the offline cases instead.
- **The organizer is trusted for presence.** The contract confirms that the organizer listed a wallet on a
  verified page. It cannot confirm that the attendee was in the room.
- **Verification tokens are derivable.** They depend only on event id and organizer address, so the
  security rests on the main-content placement, not on the token being secret.
- **Badges are not standard tokens.** `get_badge_metadata` makes a bridge possible, but this contract does
  not implement one.
- **Series completion is a read, not a snapshot.** A series badge is issued from the current state, and
  later revocations do not undo it.

## Self-review

1. Domain verification is the main new control. A mutation that checks the whole page rather than the main
   content is caught by the comments-only verification test.
2. Claims before verification: mutation caught.
3. Event-code uniqueness: mutation caught.
4. Staff cannot delegate, verify, or extend the claim window. The operator test covers all three.
5. Organizer minting respects the cancelled-event rule, the seat cap, and the duplicate-holder rule, and a
   revoked wallet cannot be re-minted. The re-mint block is enforced twice (in `organizer_mint` and in
   `_issue`), so one check alone does not remove it.
6. The non-ASCII hex bug is caught by a mutation that restores `isdigit()`.
7. Series: two events required, every event required, one claim per wallet, revocation blocks completion.
8. The v0.1 mutation checks still hold in v0.2 (wallet check, comments, rejections not consuming seats, LLM
   verdict, name check, claim window).
