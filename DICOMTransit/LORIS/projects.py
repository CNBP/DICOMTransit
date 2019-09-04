class LORIS_projects:
    @staticmethod
    def query():
        projects: list

        return projects

    @staticmethod
    def validate(project: str):
        current_projects = LORIS_projects.query()

        # Set default to false
        validation_success: bool = False

        if project in current_projects:
            validation_success = True
        else:
            validation_success = False

        return validation_success
