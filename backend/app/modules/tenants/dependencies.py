"""FastAPI dependencies for tenant-scoped requests."""

from typing import Annotated

from fastapi import Depends

from app.modules.tenants.service import TenantContext, get_current_tenant_context

TenantContextDep = Annotated[TenantContext, Depends(get_current_tenant_context)]
CurrentTenantContext = TenantContextDep
