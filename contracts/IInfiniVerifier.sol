// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title IInfiniVerifier
 * @notice EVM Smart Contract Interface for Verification-Gated Escrow Settlement (RFC-402V).
 */
interface IInfiniVerifier {
    enum EscrowStatus { Held, Settled, Refunded }

    struct EscrowHold {
        bytes32 holdId;
        address payable agentWallet;
        address payable providerAddress;
        uint256 amountWei;
        bytes32 loopfileHash;
        EscrowStatus status;
    }

    event EscrowLocked(bytes32 indexed holdId, address indexed agent, uint256 amount);
    event SettlementReleased(bytes32 indexed holdId, bytes32 indexed traceHash, address provider, uint256 amount);
    event EscrowRefunded(bytes32 indexed holdId, address indexed agent, string reason);

    /**
     * @notice Lock funds in escrow prior to step execution.
     */
    function submitEscrow(bytes32 holdId, address payable provider, bytes32 loopfileHash) external payable;

    /**
     * @notice Settle escrowed funds to provider upon submitting a verified trace proof signature.
     */
    function verifyAndSettle(
        bytes32 holdId,
        bytes32 traceHash,
        uint8 confidence,
        bytes calldata proofSig
    ) external;

    /**
     * @notice Refund escrowed funds to agent if verification fails.
     */
    function refundEscrow(bytes32 holdId, string calldata reason) external;

    /**
     * @notice Get current status of an escrow hold.
     */
    function getEscrowStatus(bytes32 holdId) external view returns (EscrowStatus status, uint256 amountWei);
}
