from settings import GH_TOKEN, GH_BASEREPO, GITUSER, GITUSEREMAIL
from github import Github, InputGitAuthor

gh = Github(GH_TOKEN)
uvrepo = gh.get_repo(GH_BASEREPO)

def uv_repo_push(path, message, content, branch, update=False):
    author = InputGitAuthor(GITUSER, GITUSEREMAIL)
    try:
        if update:
            contents = uvrepo.get_contents(path, ref=branch)
            uvrepo.update_file(contents.path, message, content, contents.sha, branch=branch, author=author)
        else:
            uvrepo.create_file(path, message, content, branch=branch, author=author)
        return True
    except:
        return False