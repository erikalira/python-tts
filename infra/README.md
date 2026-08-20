# Infrastructure

OpenTofu is the default infrastructure-as-code tool for this repository.
Docker Compose remains the runtime baseline until a concrete provider or
cluster target is selected.

The `dev`, `staging`, and `prod` environments hold an environment contract
instead of provider-specific resources. The contract records the resources each
environment must own and the runtime values the application expects from that
environment. Provider modules can be added behind this shape when an
environment has a chosen host.

The `oci` environment is the first one with real provider resources, following
the adoption rule below. It provisions the ARM64 host described in
[docs/deploy/OCI_AMPERE_A1_DEPLOY.md](../docs/deploy/OCI_AMPERE_A1_DEPLOY.md).

## Layout

- `environments/dev`: local or shared development infrastructure inventory
- `environments/staging`: production rehearsal inventory
- `environments/prod`: production inventory
- `environments/oci`: OCI Ampere A1 single-node bot host (real resources)
- `modules/environment_contract`: shared validation and outputs for the
  environment shape
- `modules/oci_bot_host`: VCN, subnet, gateway, route table, network security
  group, and Ampere A1 instance for the bot

## Local Commands

Install OpenTofu, then run the commands from each environment directory:

```powershell
tofu init -backend=false
tofu fmt -recursive ..\..
tofu validate
```

CI runs the same checks through the `Infrastructure` workflow with
`opentofu/setup-opentofu@v1`.

Do not commit `.tfstate`, `.terraform/`, `.tfvars`, or secret values. Use
environment variables, a secret manager, or CI secrets for real deployments.

## OCI Environment

The OCI environment needs provider credentials and real tenancy values:

```bash
cd environments/oci
cp terraform.tfvars.example terraform.tfvars   # gitignored; fill in your values

tofu init
tofu validate
tofu plan
tofu apply
```

Authentication comes from the OCI CLI configuration or the `OCI_CLI_*`
environment variables, not from committed files.

This module owns infrastructure only. `DISCORD_TOKEN` and `BOT_SPEAK_TOKEN` are
installed on the instance by `scripts/deploy/oci-bootstrap-env.sh` and never
appear in variables, cloud-init user data, or state.

Instance metadata, including cloud-init user data, is readable from the instance
and is stored in state. Never put a secret there.

## Provider Adoption Rule

Add a provider-specific module only after choosing the deployment target and
recording the decision in an ADR or deployment guide. Until then, keep the
module boundaries stable and let Docker Compose carry runtime execution.

The OCI module follows this rule through
[ADR 0008](../docs/adr/0008-oci-ampere-a1-deployment-target.md).
