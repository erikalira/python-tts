# Infrastructure

OpenTofu is the default infrastructure-as-code tool for this repository.
Docker Compose remains the runtime baseline until a concrete provider or
cluster target is selected.

This directory starts with an environment contract instead of provider-specific
resources. The contract records the resources each environment must own and the
runtime values the application expects from that environment. Provider modules
can be added behind this shape when dev, staging, or production has a chosen
host.

## Layout

- `environments/dev`: local or shared development infrastructure inventory
- `environments/staging`: production rehearsal inventory
- `environments/prod`: production inventory
- `modules/environment_contract`: shared validation and outputs for the
  environment shape

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

## Provider Adoption Rule

Add a provider-specific module only after choosing the deployment target and
recording the decision in an ADR or deployment guide. Until then, keep the
module boundaries stable and let Docker Compose carry runtime execution.
