import os
from typing import Generator, Iterable, Mapping
from uuid import uuid4

from .app import db


def format(uuid):
    os.system(f'ruby format.rb {uuid}')


# defining classes so type hinting works
class CourseData:
    pass


class BranchData:
    pass


class OrgData:
    pass


class UserData:
    pass


class TimeData:
    pass


class DuplicateObject(Exception):
    pass


class OrgData:
    @classmethod
    def create(cls, name: str, url: str = '', logo: str = '') -> OrgData:
        if db.exists(f"oname:{name}"):
            raise DuplicateObject

        uuid = str(int(uuid4()))

        db.hset(
            uuid,
            mapping={
                "name": name,
                "url": url,
                "logo": logo
            },
        )
        db.set(f"oname:{name}", uuid)
        return cls(uuid)

    @classmethod
    def delete(cls, name: str):
        uuid = db.get(f"oname:{name}").decode("utf-8")
        db.delete(f"oname:{name}")
        for key in db.keys(f'*{uuid}*'):
            db.delete(key)

    def __init__(self, uuid):
        self.uuid = uuid

    def __hash__(self):
        return int(self)

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)

    def __int__(self):
        return int(self.uuid)

    @classmethod
    def org(cls, name: str) -> OrgData:
        return OrgData(db.get(f"oname:{name}").decode("utf-8"))

    @property
    def name(self) -> str:
        return db.hget(self.uuid, "name").decode("utf-8")

    @name.setter
    def name(self, new_name: str):
        if db.exists(f"oname:{new_name}"):
            raise DuplicateObject
        db.delete(f"oname:{self.name}")
        db.set(f"oname:{new_name}", self.uuid)
        db.hset(self.uuid, "name", new_name)


    @property
    def url(self) -> str:
        return db.hget(self.uuid, "url").decode("utf-8")

    @url.setter
    def url(self, new_url: str):
        db.hset(self.uuid, "url", new_url)

    @property
    def logo(self) -> str:
        return db.hget(self.uuid, "logo").decode("utf-8")

    @logo.setter
    def logo(self, new_logo: str):
        db.hset(self.uuid, "logo", new_logo)

    @classmethod
    def listall(cls):
        for name in db.keys("oname:*"):
            yield cls.org(name[6:].decode("utf-8"))


class UserData:
    @classmethod
    def register(cls, name: str, bio: str = '', pfp: str = '', roles: Iterable[str] = set(),
                 courses: Iterable[CourseData] = set()) -> UserData:
        if db.exists(f"uname:{name}"):
            raise DuplicateObject

        uuid = str(int(uuid4()))

        db.hset(
            uuid,
            mapping={
                "name": name,
                "bio": bio,
                "pfp": pfp
            },
        )
        db.set(f"uname:{name}", uuid)
        for role in roles:
            db.sadd(f"roles:{uuid}", role)
        for course in courses:
            db.sadd(f"courses:{uuid}", course.uuid)
        format(uuid)
        return cls(uuid)

    @classmethod
    def delete(cls, name: str):
        uuid = db.get(f"uname:{name}").decode("utf-8")
        db.delete(f"uname:{name}")
        for key in db.keys(f'*{uuid}*'):
            db.delete(key)

    @classmethod
    def user(cls, username: str) -> UserData:
        return UserData(db.get(f"uname:{username}").decode("utf-8"))

    def __init__(self, uuid):
        self.uuid = uuid

    def __hash__(self):
        return int(self)

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)

    def __int__(self):
        return int(self.uuid)

    @property
    def name(self) -> str:
        return db.hget(self.uuid, "name").decode("utf-8")

    @name.setter
    def name(self, new_name: str):
        if db.exists(f"uname:{new_name}"):
            raise DuplicateObject
        db.delete(f"uname:{self.name}")
        db.set(f"uname:{new_name}", self.uuid)
        db.hset(self.uuid, "name", new_name)

    @property
    def bio(self) -> str:
        return db.hget(self.uuid, "bio").decode("utf-8")

    @bio.setter
    def bio(self, new_bio: str):
        db.hset(self.uuid, "bio", new_bio)
        format(self.uuid)

    @property
    def pfp(self) -> str:
        return db.hget(self.uuid, "pfp").decode("utf-8")

    @pfp.setter
    def pfp(self, new_pfp: str):
        db.hset(self.uuid, "pfp", new_pfp)

    @property
    def roles(self) -> Generator[str, None, None]:
        r = {role.decode("utf-8") for role in db.smembers(f"roles:{self.uuid}")}
        for role in r:
            if role != "Teacher":
                yield role
        if "Teacher" in r:
            yield "Teacher"


    def froles(self) -> str:
        s = ''
        for role in self.roles:
            s += f'{role}, '
        return s[:-2]

    @roles.setter
    def roles(self, new_roles: Iterable[str]):
        db.delete(f"roles:{self.uuid}")
        for role in new_roles:
            db.sadd(f"roles:{self.uuid}", role)

    @property
    def courses(self) -> Generator[CourseData, None, None]:
        for course in db.smembers(f"courses:{self.uuid}"):
            yield CourseData(course.decode("utf-8"))

    @courses.setter
    def courses(self, new_courses: Iterable[CourseData]):
        db.delete(f"courses:{self.uuid}")
        for course in new_courses:
            db.sadd(f"courses:{self.uuid}", course.uuid)

    @classmethod
    def listall(cls) -> Generator[UserData, None, None]:
        for name in db.keys("uname:*"):
            yield cls.user(name[6:].decode("utf-8"))


class CourseData:
    @classmethod
    def create(cls, name: str, description: str = '', icon: str = '') -> CourseData:

        if db.exists(f"cname:{name}"):
            raise DuplicateObject

        uuid = str(int(uuid4()))

        db.hset(
            uuid,
            mapping={
                "name": name,
                "description": description,
                "icon": icon
            },
        )
        db.set(f"cname:{name}", uuid)
        format(uuid)
        return cls(uuid)

    @classmethod
    def delete(cls, name: str):
        uuid = db.get(f"cname:{name}").decode("utf-8")
        db.delete(f"cname:{name}")
        for key in db.keys(f'*{uuid}*'):
            db.delete(key)

    @classmethod
    def course(cls, name: str) -> CourseData:
        return CourseData(db.get(f"cname:{name}").decode("utf-8"))

    @classmethod
    def listall(cls):
        for name in db.keys("cname:*"):
            yield cls.course(name[6:].decode("utf-8"))

    def __init__(self, uuid):
        self.uuid = uuid

    def __hash__(self):
        return int(self)

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)

    def __int__(self):
        return int(self.uuid)

    @property
    def name(self) -> str:
        return db.hget(self.uuid, "name").decode("utf-8")

    @name.setter
    def name(self, new_name: str):
        if db.exists(f"cname:{new_name}"):
            raise DuplicateObject
        db.delete(f"cname:{self.name}")
        db.set(f"cname:{new_name}", self.uuid)
        db.hset(self.uuid, "name", new_name)

    @property
    def description(self) -> str:
        return db.hget(self.uuid, "description").decode("utf-8")

    @description.setter
    def description(self, new_bio: str):
        db.hset(self.uuid, "description", new_bio)
        format(self.uuid)

    @property
    def icon(self) -> str:
        return db.hget(self.uuid, "icon").decode("utf-8")

    @icon.setter
    def icon(self, new_bio: str):
        db.hset(self.uuid, "icon", new_bio)

    @property
    def offered_by(self):
        chapters = set()
        for branch in BranchData.listall():
            for course in branch.courses:
                if self.uuid == course.uuid:
                    chapters.add(branch)
                    break
        return chapters



class BranchData:
    @classmethod
    def create(cls, name: str, lat: float, long: float, leader: UserData, taught: int = 0,
               raised: int = 0, email: str = '', register: str = '',
               members: Iterable[UserData] = set(), orgs: Iterable[OrgData] = set(),
               times: Mapping[CourseData, str] = dict()) -> BranchData:
        if db.exists(f"bname:{name}"):
            raise DuplicateObject

        uuid = str(int(uuid4()))

        db.hset(
            uuid,
            mapping={
                "name": name,
                "lat": lat,
                "long": long,
                "leader": leader.uuid,
                "taught": taught,
                "raised": raised,
                "email": email,
                "register": register
            },
        )
        for member in members:
            db.sadd(f"members:{uuid}", member.uuid)
        for org in orgs:
            db.sadd(f"orgs:{uuid}", org.uuid)
        if times:
            db.hset(
                f"times:{uuid}",
                mapping={course.uuid: times[course] for course in times},
            )
        db.set(f"bname:{name}", uuid)
        return cls(uuid)

    @classmethod
    def delete(cls, name: str):
        uuid = db.get(f"bname:{name}").decode("utf-8")
        db.delete(f"bname:{name}")
        for key in db.keys(f'*{uuid}*'):
            db.delete(key)

    def __init__(self, uuid):
        self.uuid = uuid

    def __hash__(self):
        return int(self)

    def __eq__(self, other):
        return type(self) == type(other) and hash(self) == hash(other)

    def __int__(self):
        return int(self.uuid)

    @classmethod
    def branch(cls, name: str) -> BranchData:
        return BranchData(db.get(f"bname:{name}").decode("utf-8"))

    @property
    def name(self):
        return db.hget(self.uuid, "name").decode("utf-8")

    @name.setter
    def name(self, new_name: str):
        if db.exists(f"bname:{new_name}"):
            raise DuplicateObject
        db.delete(f"bname:{self.name}")
        db.set(f"bname:{new_name}", self.uuid)
        db.hset(self.uuid, "name", new_name)

    @property
    def short_name(self):
        return self.name.split(',')[0]

    @property
    def lat(self) -> float:
        return float(db.hget(self.uuid, "lat").decode("utf-8"))

    @lat.setter
    def lat(self, new_lat: float):
        db.hset(self.uuid, "lat", new_lat)

    @property
    def long(self) -> float:
        return float(db.hget(self.uuid, "long").decode("utf-8"))

    @long.setter
    def long(self, new_long: float):
        db.hset(self.uuid, "long", new_long)

    @property
    def leader(self) -> UserData:
        return UserData(db.hget(self.uuid, "leader").decode("utf-8"))

    @leader.setter
    def leader(self, new_leader: UserData):
        db.hset(self.uuid, "leader", new_leader.uuid)

    @classmethod
    def listall(cls) -> Generator[BranchData, None, None]:
        for name in db.keys("bname:*"):
            if 'Basking Ridge' in name[6:].decode("utf-8"):
                yield cls.branch(name[6:].decode("utf-8"))
        for name in db.keys("bname:*"):
            if 'Basking Ridge' not in name[6:].decode("utf-8"):
                yield cls.branch(name[6:].decode("utf-8"))

    @property
    def taught(self) -> int:
        return int(db.hget(self.uuid, "taught").decode("utf-8"))

    @taught.setter
    def taught(self, new_num: int):
        db.hset(self.uuid, "taught", new_num)

    @classmethod
    def all_taught(cls) -> int:
        return sum([b.taught for b in BranchData.listall()])

    @classmethod
    def all_raised(cls) -> int:
        return sum([b.raised for b in BranchData.listall()])

    @property
    def raised(self) -> int:
        return int(db.hget(self.uuid, "raised").decode("utf-8"))

    @raised.setter
    def raised(self, new_num: int):
        db.hset(self.uuid, "raised", new_num)

    @property
    def email(self) -> str:
        return db.hget(self.uuid, "email").decode("utf-8")

    @email.setter
    def email(self, new_bio: str):
        db.hset(self.uuid, "email", new_bio)

    @property
    def register(self) -> str:
        return db.hget(self.uuid, "register").decode("utf-8")

    @register.setter
    def register(self, new_reg: str):
        db.hset(self.uuid, "register", new_reg)

    @property
    def members(self) -> Generator[UserData, None, None]:
        for member in db.smembers(f"members:{self.uuid}"):
            if any(role in (user := UserData(member.decode("utf-8"))).roles for role in {'Founder', 'Co-Founder', 'Chapter Leader'}):
                yield user
        for member in db.smembers(f"members:{self.uuid}"):
            if not any(role in (user := UserData(member.decode("utf-8"))).roles for role in {'Founder', 'Co-Founder', 'Chapter Leader', 'Teacher'}):
                yield user
        for member in db.smembers(f"members:{self.uuid}"):
            if (not any(role in (user := UserData(member.decode("utf-8"))).roles for role in {'Founder', 'Co-Founder', 'Chapter Leader'})) and ('Teacher' in user.roles):
                yield user

    @members.setter
    def members(self, new_members: Iterable[UserData]):
        db.delete(f"members:{self.uuid}")
        for member in new_members:
            db.sadd(f"members:{self.uuid}", member.uuid)

    @property
    def orgs(self) -> Generator[OrgData, None, None]:
        for org in db.smembers(f"orgs:{self.uuid}"):
            yield OrgData(org.decode("utf-8"))

    @orgs.setter
    def orgs(self, new_orgs: Iterable[OrgData]):
        db.delete(f"orgs:{self.uuid}")
        for org in new_orgs:
            db.sadd(f"orgs:{self.uuid}", org.uuid)

    @property
    def times(self):
        timedict = db.hgetall(f"times:{self.uuid}")
        return {k.decode("utf-8") : v.decode("utf-8") for k, v in timedict.items()}

    @times.setter
    def times(self, timedict):
        db.hset(
            f"times:{self.uuid}",
            mapping={k.uuid: v for k, v in timedict.items()}
        )

    def time(self, course):
        try:
            return self.times[course.uuid]
        except KeyError:
            return "TBD"

    @property
    def courses(self) -> Generator[CourseData, None, None]:
        s = set()
        for member in self.members:
            for course in member.courses:
                s.add(course.uuid)
        for element in s:
            yield CourseData(element)

    def taught_by(self, course):
        s = set()
        for member in self.members:
            if course.name in {c.name for c in member.courses}:
                s.add(member.uuid)
        for element in s:
            yield UserData(element)
