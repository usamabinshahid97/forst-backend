import os
from typing import List, Union

from pydantic import AnyHttpUrl, BaseModel, validator

class Settings(BaseModel):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("API_SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    
    # 60 minutes * 24 hours * 7 days = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:password@localhost/ecommerce_admin"
    )
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

settings = Settings() 