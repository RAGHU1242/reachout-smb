from typing import Optional, List
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.session import get_db
from app.core.security import decode_access_token
from app.models.models import User, BusinessMember, Business
from app.models.enums import RoleEnum

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user

async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    return result.scalar_one_or_none()

async def get_current_business(
    x_business_id: Optional[str] = Header(None, alias="X-Business-Id"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Business:
    """
    Enforces strict tenant isolation: verifies that the authenticated user
    is an authorized member of the requested business.
    """
    if not x_business_id:
        # If header not provided, find the user's primary/first business
        membership_res = await db.execute(
            select(BusinessMember).where(BusinessMember.user_id == current_user.id).limit(1)
        )
        membership = membership_res.scalar_one_or_none()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No business found for user. Please complete business onboarding.",
            )
        x_business_id = membership.business_id

    # Verify authorization
    query = (
        select(Business)
        .join(BusinessMember, BusinessMember.business_id == Business.id)
        .where(
            Business.id == x_business_id,
            BusinessMember.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You are not a member of this business tenant.",
        )
    return business

def require_roles(allowed_roles: List[RoleEnum]):
    async def role_checker(
        current_user: User = Depends(get_current_user),
        business: Business = Depends(get_current_business),
        db: AsyncSession = Depends(get_db)
    ) -> BusinessMember:
        result = await db.execute(
            select(BusinessMember).where(
                BusinessMember.business_id == business.id,
                BusinessMember.user_id == current_user.id
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this business",
            )
        if member.role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Action requires one of roles: {[r.value for r in allowed_roles]}",
            )
        return member
    return role_checker
