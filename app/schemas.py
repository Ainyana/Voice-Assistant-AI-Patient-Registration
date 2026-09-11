import re
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

US_STATES = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"}
SEX_VALUES = {"Male", "Female", "Other", "Decline to Answer"}

def normalize_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError("Phone number must contain 10 US digits")
    return digits

class PatientBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    date_of_birth: date
    sex: str
    phone_number: str
    email: Optional[EmailStr] = None
    address_line_1: str = Field(min_length=1, max_length=255)
    address_line_2: Optional[str] = None
    city: str = Field(min_length=1, max_length=100)
    state: str
    zip_code: str
    insurance_provider: Optional[str] = None
    insurance_member_id: Optional[str] = None
    preferred_language: Optional[str] = "English"
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("first_name", "last_name")
    @classmethod
    def names(cls, v):
        v = v.strip()
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", v): raise ValueError("Name contains invalid characters")
        return v
    @field_validator("date_of_birth")
    @classmethod
    def dob(cls, v):
        if v > date.today(): raise ValueError("Date of birth cannot be in the future")
        return v
    @field_validator("sex")
    @classmethod
    def sex_value(cls, v):
        if v not in SEX_VALUES: raise ValueError("Invalid sex value")
        return v
    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def phone(cls, v): return normalize_phone(v) if v is not None else v
    @field_validator("state")
    @classmethod
    def state_value(cls, v):
        v = v.upper().strip()
        if v not in US_STATES: raise ValueError("Invalid US state abbreviation")
        return v
    @field_validator("zip_code")
    @classmethod
    def zip_value(cls, v):
        if not re.fullmatch(r"\d{5}(-\d{4})?", v): raise ValueError("Invalid ZIP code")
        return v

class PatientCreate(PatientBase): pass
class PatientUpdate(BaseModel):
    first_name: Optional[str] = None; last_name: Optional[str] = None; date_of_birth: Optional[date] = None; sex: Optional[str] = None; phone_number: Optional[str] = None; email: Optional[EmailStr] = None; address_line_1: Optional[str] = None; address_line_2: Optional[str] = None; city: Optional[str] = None; state: Optional[str] = None; zip_code: Optional[str] = None; insurance_provider: Optional[str] = None; insurance_member_id: Optional[str] = None; preferred_language: Optional[str] = None; emergency_contact_name: Optional[str] = None; emergency_contact_phone: Optional[str] = None
    @field_validator("phone_number", "emergency_contact_phone")
    @classmethod
    def phone(cls, v): return normalize_phone(v) if v is not None else v
    @field_validator("state")
    @classmethod
    def state_value(cls, v):
        if v is None: return v
        v=v.upper().strip()
        if v not in US_STATES: raise ValueError("Invalid US state abbreviation")
        return v
    @field_validator("date_of_birth")
    @classmethod
    def dob(cls, v):
        if v and v > date.today(): raise ValueError("Date of birth cannot be in the future")
        return v
class PatientResponse(PatientBase):
    patient_id: str; created_at: datetime; updated_at: datetime; deleted_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
