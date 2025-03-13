from pydantic import BaseModel

class Candidate(BaseModel):
    name: str
    email: str
    skills: list[str]
    certificates: list[str]
    education: list[str]
    experiences: list[str]

    def flatten(self):
        return {
            "name": self.name,
            "email": self.email,
            "skills": ",".join(self.skills) if len(self.skills)>0 else "",
            "certificates": ",".join(self.certificates) if len(self.certificates) > 0 else "",
            "education": ",".join(self.education) if len(self.education) > 0 else "",
            "experiences": ",".join(self.experiences) if len(self.experiences) > 0 else ""
        }