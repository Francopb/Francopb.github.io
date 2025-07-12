import os, yaml
from jinja2 import Environment, FileSystemLoader

DATA_DIR = "data"
DOCS_DIR = "docs"
TEMPLATES_DIR = "templates"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

def load_yaml(dir_name):
    data = {}
    for file in os.listdir(dir_name):
        print(f"Loading {file}")
        if file.endswith(".yaml"):
            with open(os.path.join(dir_name, file)) as f:
                item = yaml.safe_load(f)
                data[item["id"]] = item
    return data

def render(template_name, context, output_path):
    template = env.get_template(template_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"Rendenring {output_path}")
    with open(output_path, "w") as f:
        f.write(template.render(context))

def main():
    with open("data/profile.yaml") as f:
        profile = yaml.safe_load(f)

    # Render homepage
    render(
        "index.md.j2",
        profile,
        f"{DOCS_DIR}/index.md"
    )

    # Render contact page
    render(
        "contact.md.j2",
        profile,
        f"{DOCS_DIR}/contact.md"
    )

    topics = load_yaml(f"{DATA_DIR}/topics")
    projects = load_yaml(f"{DATA_DIR}/projects")
    publications = load_yaml(f"{DATA_DIR}/publications")
    conferences = load_yaml(f"{DATA_DIR}/conferences")

    # Generate project index page
    active_projects = []
    inactive_projects = []

    for project in projects.values():
        status = project.get("status", "active")  # Default to active
        if status == "active":
            active_projects.append(project)
        else:
            inactive_projects.append(project)

    # Sort projects by title or year if needed
    active_projects.sort(key=lambda x: x["title"])
    inactive_projects.sort(key=lambda x: x["title"])

    render(
        "projects_index.md.j2",
        {
            "active_projects": active_projects,
            "inactive_projects": inactive_projects,
        },
        f"{DOCS_DIR}/projects/index.md"
    )

    project_list = active_projects + inactive_projects

    for i, project in enumerate(project_list):
        related_topics =[
            topics[tid] for tid in project.get("topics", []) if tid in topics
        ]

        related_pubs = [
            pub for pub in publications.values() if project["id"] in pub.get("projects", [])
        ]
        related_pubs.sort(key=lambda x: x.get("year", 0), reverse=True)

        # Filter and sort related conferences
        related_confs = [
            conf for conf in conferences.values() if project["id"] in conf.get("projects", [])
        ]
        related_confs.sort(key=lambda x: x.get("year", 0), reverse=True)

        prev_project = project_list[(i - 1) % len(project_list)]
        next_project = project_list[(i + 1) % len(project_list)]

        render(
            "project.md.j2",
            {
                "project": project,
                # "related_topics": related_topics,
                "related_pubs": related_pubs,
                "related_confs": related_confs,
                "prev_project": prev_project,
                "next_project": next_project,
            },
            f"{DOCS_DIR}/projects/{project['id']}.md"
        )

    # for topic in topics.values():
    #     related_proj = [
    #         proj for proj in projects.values()
    #         if topic["id"] in proj.get("topics", [])
    #     ]

    #     render(
    #         "topic.md.j2", 
    #         {
    #             "topic": topic,
    #             "related_proj": related_proj,
    #         },
    #         f"{DOCS_DIR}/topics/{topic['id']}.md")

    # sorted_topics = sorted(topics.values(), key=lambda x: x["title"])
    # render("topics_index.md.j2", {"topics": sorted_topics}, f"{DOCS_DIR}/topics/index.md")

    sorted_pubs = sorted(publications.values(), key=lambda x: x.get("year", 0), reverse=True)
    sorted_confs = sorted(conferences.values(), key=lambda x: x.get("year", 0), reverse=True)

    render(
        "publications_and_conferences.md.j2",
        {
            "publications": sorted_pubs,
            "conferences": sorted_confs,
        },
        f"{DOCS_DIR}/publications/index.md"
    )

    # Load mkdocs.yml
    with open("mkdocs_base.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    project_files = []
    for project in project_list:
        print(project["title"])
        # print(project["id"])
        project_files.append({project["title"]: f"projects/{project['id']}.md"})

    # Find and replace the Projects section
    for i, item in enumerate(config["nav"]):
        if isinstance(item, dict) and "Projects" in item:
            # Replace existing projects list
            config["nav"][i] = {
                "Projects": [{"Overview": "projects/index.md"}] + project_files
            }
            break

    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    main()
