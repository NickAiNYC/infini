use anchor_lang::prelude::*;

declare_id!("InfiniVerifier111111111111111111111111111111");

#[program]
pub mod infini_verifier {
    use super::*;

    pub fn lock_escrow(
        ctx: Context<LockEscrow>,
        hold_id: [u8; 32],
        amount: u64,
        loopfile_hash: [u8; 32],
    ) -> Result<()> {
        let hold = &mut ctx.accounts.escrow_hold;
        hold.agent = ctx.accounts.agent.key();
        hold.provider = ctx.accounts.provider.key();
        hold.amount = amount;
        hold.loopfile_hash = loopfile_hash;
        hold.status = 0; // Held
        Ok(())
    }

    pub fn settle_verified(
        ctx: Context<SettleVerified>,
        _trace_hash: [u8; 32],
        confidence: u8,
    ) -> Result<()> {
        require!(confidence >= 80, InfiniError::VerificationFailed);
        let hold = &mut ctx.accounts.escrow_hold;
        hold.status = 1; // Settled
        **ctx.accounts.escrow_hold.to_account_info().try_borrow_mut_lamports()? -= hold.amount;
        **ctx.accounts.provider.to_account_info().try_borrow_mut_lamports()? += hold.amount;
        Ok(())
    }
}

#[account]
pub struct EscrowHold {
    pub agent: Pubkey,
    pub provider: Pubkey,
    pub amount: u64,
    pub loopfile_hash: [u8; 32],
    pub status: u8,
}

#[derive(Accounts)]
pub struct LockEscrow<'info> {
    #[account(init, payer = agent, space = 8 + 32 + 32 + 8 + 32 + 1)]
    pub escrow_hold: Account<'info, EscrowHold>,
    #[account(mut)]
    pub agent: Signer<'info>,
    /// CHECK: Safe provider address
    pub provider: AccountInfo<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct SettleVerified<'info> {
    #[account(mut)]
    pub escrow_hold: Account<'info, EscrowHold>,
    /// CHECK: Provider receiving lamports
    #[account(mut)]
    pub provider: AccountInfo<'info>,
}

#[error_code]
pub enum InfiniError {
    #[msg("Verification confidence score does not meet threshold.")]
    VerificationFailed,
}
