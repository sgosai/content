import abc
import datetime
import json
import sys
import yaml

from Tests.test_utils import print_error

contentLibPath = "./"
limitedVersion = False

LAYOUT_TYPE_TO_NAME = {
    "details": "Summary",
    "edit": "New/Edit",
    "close": "Close",
}

INTEGRATIONS_DIR = "Integrations"
SCRIPTS_DIR = "Scripts"
PLAYBOOKS_DIR = "Playbooks"
REPORTS_DIR = "Reports"
DASHBOARDS_DIR = "Dashboards"
WIDGETS_DIR = "Widgets"
INCIDENT_FIELDS_DIR = "IncidentFields"
LAYOUTS_DIR = "LAYOUTS"
CLASSIFIERS_DIR = "Classifiers"
REPUTATIONS_DIR = "Misc"

RELEASE_NOTES_ORDER = [INTEGRATIONS_DIR, SCRIPTS_DIR, PLAYBOOKS_DIR, REPORTS_DIR,
                       DASHBOARDS_DIR, WIDGETS_DIR, INCIDENT_FIELDS_DIR, LAYOUTS_DIR,
                       CLASSIFIERS_DIR, REPUTATIONS_DIR]


def add_dot(text):
    if text.endswith('.'):
        return text
    return text + '.'


def release_notes_item(header, body):
    return '__' + header + '__\n' + add_dot(body) + '\n'


class Content:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.modified_store = []
        self.added_store = []
        self.deleted_store = []

    def add(self, change_type, data):
        if change_type == "M":
            self.modified_store.append(data)
        elif change_type == "A":
            self.added_store.append(data)
        elif change_type == "D":
            self.deleted_store.append(data)
        else:
            print "Unknown change type " + change_type

    @abc.abstractmethod
    def get_header(self):
        return

    @abc.abstractmethod
    def added_release_notes(self, data):
        return

    @abc.abstractmethod
    def modified_release_notes(self, data):
        return

    @abc.abstractmethod
    def load_data(self, data):
        return
    
    def show_secondary_header(self):
        return True

    def generate_release_notes(self):
        res = ""
        missing_release_notes = False

        if len(self.modified_store) + len(self.deleted_store) + len(self.added_store) > 0:
            section_body = ""
            if len(self.added_store) > 0:
                new_str = ""
                new_count = 0
                for raw_content in self.added_store:
                    cnt = self.load_data(raw_content)

                    ans = self.added_release_notes(cnt)
                    if ans is None:
                        print_error(cnt["name"] + " is missing releaseNotes entry")
                        missing_release_notes = True

                    if ans:
                        new_count += 1
                    new_str += ans

                if len(new_str) > 0:
                    if self.show_secondary_header():
                        if new_count > 1:
                            section_body += "\n##### " + str(new_count) + " New " + self.get_header() + "\n"
                        else:
                            section_body += "\n##### New " + self.get_header() + "\n"
                    section_body += new_str
            if len(self.modified_store) > 0:
                modified_str = ""
                modified_count = 0
                for raw_content in self.modified_store:
                    cnt = self.load_data(raw_content)
                    ans = self.modified_release_notes(cnt)
                    if ans is None:
                        print_error(cnt["name"] + " is missing releaseNotes entry")
                        missing_release_notes = True
                    elif ans is not "":
                        modified_str += ans
                        modified_count += 1
                if len(modified_str) > 0:
                    if self.show_secondary_header():
                        if modified_count > 1:
                            section_body += "\n##### " + str(modified_count) + " Improved " + self.get_header() + "\n"
                        else:
                            section_body += "\n##### Improved " + self.get_header() + "\n"
                    section_body += modified_str
            if len(self.deleted_store) > 0:
                section_body += "\n##### Removed " + self.get_header() + "\n"
                for raw_content in self.deleted_store:
                    section_body += "- " + raw_content + "\n"

            if missing_release_notes:
                return None
            if len(section_body) > 0:
                res = "### " + self.get_header() + "\n"
                res += section_body

        return res


class ScriptContent(Content):

    def load_data(self, data):
        return yaml.safe_load(data)

    def get_header(self):
        return "Scripts"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) > 0 and rn == "-":
            return ""
        return release_notes_item(cnt["name"], cnt["comment"])

    def modified_release_notes(self,cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], rn)
        return res


Content.register(ScriptContent)


class PlaybookContent(Content):
    def load_data(self, data):
        return yaml.safe_load(data)

    def get_header(self):
        return "Playbooks"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) > 0 and rn == "-":
            return ""
        
        return release_notes_item(cnt["name"], cnt["description"])

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], rn)
        return res


Content.register(PlaybookContent)


class ReportContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Reports"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) > 0 and rn == "-":
            return ""
        return release_notes_item(cnt["name"], cnt["description"])

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], rn)
        return res


Content.register(ReportContent)


class DashboardContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Dashboards"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) > 0 and rn == "-":
            return ""
        
        return release_notes_item(cnt["name"], cnt["description"])

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], rn)
        return res


Content.register(DashboardContent)


class WidgetContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Widgets"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) > 0 and rn == "-":
            return ""
        
        return release_notes_item(cnt["name"], cnt["description"])

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], rn)
        return res


Content.register(WidgetContent)


class IncidentFieldContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Incident Fields"

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None

        return add_dot(rn) + "\n"

    def show_secondary_header(self):
        return False

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = add_dot(rn) + "\n"
        return res


Content.register(IncidentFieldContent)


class LayoutContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Incident Layouts"

    @staticmethod
    def get_release_notes(cnt):
        rn = cnt.get("releaseNotes", "")

        layout_kind = LAYOUT_TYPE_TO_NAME.get(cnt.get("kind", ""))
        if not layout_kind:
            print_error("invalid layout kind %s" % (cnt.get("kind", ""),))
            return None

        layout_type = cnt.get("typeId")
        if not layout_type:
            print_error("invalid layout kind %s" % (layout_type,))
            return None

        return release_notes_item(layout_type + " - " + layout_kind, rn)

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None

        return LayoutContent.get_release_notes(cnt)

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")

        if len(rn) == 0:
            return None

        if rn == "-":
            return ""

        return LayoutContent.get_release_notes(cnt)


Content.register(LayoutContent)


class ClassifierContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Classification & Mapping"

    @staticmethod
    def get_release_notes(cnt):
        rn = cnt.get("releaseNotes", "")
        brand_name = cnt.get("brandName")
        if not brand_name:
            print_error("invalid classifier brand name %s" % (brand_name,))
            return None

        return release_notes_item(brand_name, rn)

    def added_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None

        return ClassifierContent.get_release_notes(cnt)

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")

        if len(rn) == 0:
            return None

        if rn == "-":
            return ""

        return ClassifierContent.get_release_notes(cnt)


Content.register(ClassifierContent)


class ReputationContent(Content):
    def load_data(self, data):
        return json.loads(data)

    def get_header(self):
        return "Reputations"

    def added_release_notes(self, cnt):
        # This should never happen
        return ""

    def show_secondary_header(self):
        return False

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = cnt["releaseNotes"] + "\n"
        return res


Content.register(ReputationContent)


class IntegrationContent(Content):
    def load_data(self, data):
        return yaml.safe_load(data)

    def get_header(self):
        return "Integrations"

    def added_release_notes(self, cnt):
        return release_notes_item(cnt["name"], cnt["description"])

    def modified_release_notes(self, cnt):
        rn = cnt.get("releaseNotes", "")
        if len(rn) == 0:
            return None
        res = ""

        if rn != '-':
            res = release_notes_item(cnt["name"], cnt["releaseNotes"])
        return res


Content.register(IntegrationContent)


release_note_generator = {
    INTEGRATIONS_DIR: IntegrationContent(),
    SCRIPTS_DIR: ScriptContent(),
    PLAYBOOKS_DIR: PlaybookContent(),
    REPORTS_DIR: ReportContent(),
    DASHBOARDS_DIR: DashboardContent(),
    WIDGETS_DIR: WidgetContent(),
    INCIDENT_FIELDS_DIR: IncidentFieldContent(),
    LAYOUTS_DIR: LayoutContent(),
    CLASSIFIERS_DIR: ClassifierContent(),
    REPUTATIONS_DIR: ReputationContent()
}


def parse_change_list(file_path):
    with open(file_path, 'r') as f:
        data = f.read()
        return data.split("\n")
    return []


def get_deleted_content(full_file_name, data):
    start_index = data.find(full_file_name)
    if start_index > 0:
        name_index = data.find("-name:", start_index)
        if name_index > 0:
            return data[name_index:].split("\n")[0][len("-name:"):].strip()
    return ""


def handle_deleted_files(delete_file_path, full_file_name):
    with open(delete_file_path, 'r') as f:
        data = f.read()
        if "/" in full_file_name:
            file_type = full_file_name.split("/")[0]
            file_type_mapping = release_note_generator.get(file_type)
            deleted_content = get_deleted_content(full_file_name, data)
            if file_type_mapping is not None:
                file_type_mapping.add("D", deleted_content)


def create_file_release_notes(file_name, delete_file_path):
    if len(file_name) > 0:
        names = file_name.split("\t")
        change_type = names[0]
        full_file_name = names[1]

        if not "/" in full_file_name:
            return

        file_type = full_file_name.split("/")[0]
        file_type_mapping = release_note_generator.get(file_type)
        if file_type_mapping is None:
            print "Unsupported file type " + file_type
            return

        if change_type == "D":
            handle_deleted_files(delete_file_path, full_file_name)
        elif change_type != "R100" and change_type != "R094":
            if change_type == "R093" or change_type == "R098" or change_type == "R078":
                # handle the same as modified
                full_file_name = names[2]
                change_type = 'M'

            with open(contentLibPath + full_file_name, 'r') as f:
                data = f.read()
                file_type_mapping.add(change_type, data)


def create_content_descriptor(version, asset_id, res):
    # time format example 2017 - 06 - 11T15:25:57.0 + 00:00
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.0+00:00")
    release_notes = "## Demisto Content Release Notes for version " + version + " (" + asset_id + ")\n"
    release_notes += "##### Published on %s\n%s" % (datetime.datetime.now().strftime("%d %B %Y"), res)
    content_descriptor = {
        "installDate": "0001-01-01T00:00:00Z",
        "assetId": int(asset_id),
        "releaseNotes": release_notes,
        "modified": date,
        "ignoreGit": False,
        "releaseDate": date,
        "version": -1,
        "release": version,
        "id": ""
    }
    with open('content-descriptor.json', 'w') as outfile:
        json.dump(content_descriptor, outfile)

    with open('release-notes.txt', 'w') as outfile:
        outfile.write(release_notes)


def main(argv):
    if len(argv) < 4:
        print "<Release version>, <File with the full list of changes>, " \
              "<Complete diff file for deleted files>, <assetID>"
        sys.exit(1)
    files = parse_change_list(argv[1])

    for file in files:
        create_file_release_notes(file, argv[2])

    res = ""
    missing_release_notes = False
    for key in RELEASE_NOTES_ORDER:
        value = release_note_generator[key]
        ans = value.generate_release_notes()
        print "%%%%%%%%%%%%%%%"
        print "** ans **"
        print ans
        print "***"
        if ans is None:
            missing_release_notes = True
        else:
            if len(res) > 0:
                res += "\n---\n"
            print "** res **"
            print res
            print "***"
            print "%%%%%%%%%%%%%%%%"
            res += ans
    if missing_release_notes:
        sys.exit(1)
    version = argv[0]
    asset_id = argv[3]
    create_content_descriptor(version, asset_id, res)


if __name__ == "__main__":
    main(sys.argv[1:])
