from mastodon import Mastodon

from django.conf import settings
from os import urandom, path, mkdir
from base64 import b64encode

from mastodon_sync.models import Account

_mastodonHandles = {}


def post(account, body, isNsfw):
    mastodon = _getMastodonHandle(account)
    mastodon.status_post(body, sensitive=isNsfw)


def postToMainAccount(body, isNsfw):
    _getMainMastodonHandle().status_post(body, sensitive=isNsfw)


def _getMastodonHandle(account):
    username = account.username
    if username not in _mastodonHandles:
        _mastodonHandles[username] = _createSession(account)
    mastodon = _mastodonHandles[username]
    return mastodon


def _getMainMastodonHandle():
    directory = "tokens"
    if not path.exists(directory):
        mkdir(directory)
    tokenPath = path.join(directory, '{}.token'.format(settings.MASTODON['USERNAME']))
    if not path.exists(tokenPath):
        mastodon = Mastodon(client_id=settings.MASTODON['CLIENT_ID'],
                            client_secret=settings.MASTODON['CLIENT_SECRET'],
                            api_base_url=settings.MASTODON['BASE_URL'])
        mastodon.log_in(username=settings.MASTODON['EMAIL'],
                        password=settings.MASTODON['PASSWORD'],
                        scopes=['read', 'write'],
                        to_file=tokenPath)
    mastodon = Mastodon(
        access_token=tokenPath,
        api_base_url=settings.MASTODON['BASE_URL']
    )
    return mastodon


def _createSession(account):
    directory = "tokens"
    if not path.exists(directory):
        mkdir(directory)
    tokenPath = path.join(directory, '{}.token'.format(account.username))
    if not path.exists(tokenPath):
        print("Creating token file for {}".format(account.username))
        mastodon = Mastodon(client_id=settings.MASTODON['CLIENT_ID'],
                            client_secret=settings.MASTODON['CLIENT_SECRET'],
                            api_base_url=settings.MASTODON['BASE_URL'])
        print(account.email)
        print(account.password)
        mastodon.log_in(username=account.email,
                        password=account.password,
                        scopes=['read', 'write'],
                        to_file=tokenPath)
    mastodon = Mastodon(
        access_token=tokenPath,
        api_base_url=settings.MASTODON['BASE_URL']
    )
    return mastodon


def getAccount(username):
    try:
        return Account.objects.get(username=username)
    except Account.DoesNotExist:
        return None


def createAccount(username, isNsfw, subreddit):
    mastodon = Mastodon(client_id=settings.MASTODON['CLIENT_ID'],
                        client_secret=settings.MASTODON['CLIENT_SECRET'],
                        api_base_url=settings.MASTODON['BASE_URL'])
    email = "r_{}_bot@{}".format(username.lower(), settings.MASTODON['EMAIL_DOMAIN']),
    account = Account(
        username=username,
        email=email,
        password=settings.MASTODON['DEFAULT_PASSWORD'],
        subreddit=subreddit
    )
    account.save()
    try:
        mastodon.create_account(
            account.username,
            account.password,
            account.email,
            agreement=True,
            locale='en',
            scopes=['read', 'write'],
            to_file=path.join("tokens", "{}.token".format(account.username))
        )
        baseUrl = settings.MASTODON['BASE_URL'].replace("https://", "").replace("http://", "")
        postBody = "@{}@{} is now available to follow!".format(account.username, baseUrl)
        postToMainAccount(postBody, isNsfw)
    except Exception as e:
        # Check if user already exists with the default password
        sessionHandle = _getMastodonHandle(account)
        statuses = sessionHandle.account_statuses(sessionHandle.account_verify_credentials()['id'], limit=1)
        if len(statuses) > 0:
            status = statuses[0]
            for post in subreddit.post_set.all().order_by('created'):
                if post.reddit_url in status.content:
                    account.lastInserted = post.id
                    account.save()
                    break

    return account


def getNewMentions():
    mastodon = _getMainMastodonHandle()
    notifications = mastodon.notifications()
    bodies = []
    for n in notifications:
        if n["type"] == "mention":
            bodies.append(n["status"]["content"])
            mastodon.notifications_dismiss(n["id"])
    return bodies


def getNewMessages():
    mastodon = _getMainMastodonHandle()
    convos = mastodon.conversations()
    bodies = []
    for c in convos:
        if c["unread"]:
            bodies.append(c["last_status"]["content"])
            mastodon.conversations_read(c["id"])
    return bodies


def getLocalFollowers():
    mastodon = _getMainMastodonHandle()
    followers = mastodon.account_followers(mastodon.account_verify_credentials()['id'])
    ret = []
    for f in followers:
        if not "@" in f.acct:
            ret.append(f.acct)
    return ret
