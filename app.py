import os
os.environ["WANDB_SILENT"] = "true"

import json
import sys
import click

import pandas as pd
from github import Github

from label_bot import models



def init_models(ctx, param, value):
    global BOT

    if not value or ctx.resilient_parsing:
        BOT = models.Bot(use_head=False)
    else:
        BOT = models.Bot(use_head=True)


@click.group()
@click.option("--use-head", "-h", is_flag=True, callback=init_models, expose_value=False)
def cli():
    pass


def get_token(file="token.json"):
    with open(file) as f:
        token = json.load(f)["token"]

    return token


def predict(title, body):
    return BOT.predict(title, body)[0]


@cli.command("crawl-organization")
@click.option("--organization", "-O")
def run_on_org(organization):
    results = pd.DataFrame(columns=["repo", "issue", "bug", "question", "enhancement"])

    token = get_token()
    g = Github(token)

    root = g.get_organization(organization)

    for repo in root.get_repos():
        for issue in repo.get_issues():
            b_score, q_score, e_score = predict(issue.title, issue.body)
            results = results.append({"repo" : repo.name,
                                      "issue" : issue.number,
                                      "bug" : b_score,
                                      "question" : q_score,
                                      "enhancement" : e_score
                                    }, ignore_index=True)

    return results


@cli.command("crawl-user")
@click.option("--user", "-U")
def run_on_user(user):
    results = pd.DataFrame(columns=["repo", "issue", "bug", "question", "enhancement"])

    token = get_token()
    g = Github(token)

    root = g.get_user(user)

    for repo in root.get_repos():
        for issue in repo.get_issues():
            b_score, q_score, e_score = predict(issue.title, issue.body)
            results = results.append({"repo" : repo.name,
                                      "issue" : issue.number,
                                      "bug" : b_score,
                                      "question" : q_score,
                                      "enhancement" : e_score
                                    }, ignore_index=True)

    return results


@cli.command("crawl-repo")
@click.option("--repo", "-R")
def run_on_repo(repo):
    results = pd.DataFrame(columns=["repo", "issue", "bug", "question", "enhancement"])

    token = get_token()
    g = Github(token)

    repo = g.get_repo(repo)

    for issue in repo.get_issues():
        b_score, q_score, e_score = predict(issue.title, issue.body)
        results = results.append({"repo" : repo.name,
                                  "issue" : issue.number,
                                  "bug" : b_score,
                                  "question" : q_score,
                                  "enhancement" : e_score
                                }, ignore_index=True)

    return results


@cli.command("crawl-issue")
@click.option("--repo", "-R")
@click.option("--issue", "-I")
def run_on_issue(repo, issue):
    results = pd.DataFrame(columns=["repo", "issue", "bug", "question", "enhancement"])

    token = get_token()
    g = Github(token)

    repo = g.get_repo(repo)
    issue = repo.get_issue(number=issue)

    b_score, q_score, e_score = predict(issue.title, issue.body)
    results = results.append({"repo" : repo.name,
                              "issue" : issue.number,
                              "bug" : b_score,
                              "question" : q_score,
                              "enhancement" : e_score
                            }, ignore_index=True)

    return results


def demo():
    title = input("Title: ")
    body = input("Body: ")

    scores = predict(title, body)

    for kind, score in zip(("Bug", "Question", "Enhancement"), scores):
        print(f"{kind}: {score}")
    print()

    keep_going = input("Try another one? [y/n] ")

    while keep_going not in ("y", "n"):
      print("Type 'y' for YES or 'n' for NO")
      keep_going = input("Try another one? [y/n] ")

    if keep_going == "y":
        demo()
    else:
        sys.exit()


@cli.command("demo")
def start_demo():
    demo()



if __name__ == "__main__":
    cli()
