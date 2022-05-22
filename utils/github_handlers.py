from settings import GH_TOKEN, GH_BASEREPO, GITUSER, GITUSEREMAIL, GH_MET_BRANCH
from github import Github, InputGitAuthor

gh = Github(GH_TOKEN)
uvrepo = gh.get_repo(GH_BASEREPO)

def uv_repo_push(path, message, content, update=False):
    author = InputGitAuthor(GITUSER, GITUSEREMAIL)
    try:
        if update:
            contents = uvrepo.get_contents(path, ref=GH_MET_BRANCH)
            uvrepo.update_file(contents.path, message, content, contents.sha, branch=GH_MET_BRANCH, author=author)
        else:
            uvrepo.create_file(path, message, content, branch=GH_MET_BRANCH, author=author)
        return True
    except:
        return False


def commit_string_maker(if_update, user, template_info):
    commit_text = "UV record "
    if if_update:
        commit_text += "edit "
    else:
        commit_text += "init creation "
    commit_text += user.email.split('@')[0] + '. Schema: ' + template_info[1] + ' ' + template_info[2] + '.'
    return commit_text