
class Status:
    GENERATED = "generated"
    FINISHED = "finished"
    ACTIVE = "active"
    FINAL = "final"

class Gender:
    MALE = "male"
    FEMALE = "female"

    def get_all(self):
        return [self.MALE, self.FEMALE]
