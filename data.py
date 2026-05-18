from typing import TypedDict

class CourseDetail(TypedDict):
    url: str # use as primary key
    title: str
    cost: float # in THB
    overview: str
    instructor_name: str
    avg_rating: float # from 0 to 5
    total_reviews: int
    overall_satisfaction_percentage: int # from 0 to 100
    review_highlight_percentages: dict[str, int] # label -> percentage from 0 to 100

class CourseCategory(TypedDict):
    url: str
    category: str

class CourseReviewHighlight(TypedDict):
    url: str
    label: str
    percentage: int # from 0 to 100

class InstructorDetail(TypedDict, total=False):
    name: str
    position: str # if any. the instructor can be institute or company

