from typing import TypedDict

class CourseDetail(TypedDict):
    url: str # use as primary key
    title: str
    cost: int # in THB
    overview: str
    instructor_name: str
    avg_rating: float # from 0 to 5
    total_reviews: int

class CourseCategory(TypedDict):
    course_url: str
    category: str

class InstructorDetail(TypedDict):
    name: str
    position: str