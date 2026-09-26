# personal-sync-agent

An hourly GitHub Action reads recent unread Gmail messages from one sender with `updates` in the subject, asks an OpenAI model for proposed file contents, and opens a **draft pull request**. A person reviews and merges each proposal. It processes up to 10 messages per run and marks a message read only after creating the PR or deciding there are no actionable changes.

## Install

Copy `main.py`, `requirements.txt`, `tests/`, `.gitignore`, and `.github/workflows/sync.yml` into the root of the GitHub repository you want to update. The workflow runs against that repository's default branch. Create and merge a normal PR containing these files first.

1. In [Google Cloud Console](https://console.cloud.google.com/), create a project, enable the **Gmail API**, configure the OAuth consent screen, and create a **Desktop app OAuth client**. Add your Gmail account as a test user if the app is in testing. Download the OAuth client JSON privately; never commit it.
2. Obtain an **authorized-user OAuth token** for the same account with the scope `https://www.googleapis.com/auth/gmail.modify` and offline access. For example, on your own computer, install `google-auth-oauthlib`, then run this one-time script beside the downloaded client JSON:

   ```python
   from google_auth_oauthlib.flow import InstalledAppFlow
   flow = InstalledAppFlow.from_client_secrets_file(
       "client_secret.json", ["https://www.googleapis.com/auth/gmail.modify"]
   )
   credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
   print(credentials.to_json())
   ```

   Save the printed JSON privately. It must contain a `refresh_token`. For unattended use, publish the OAuth app to production if appropriate; a Google OAuth app in **Testing** can have short-lived refresh tokens. Use the account's own mailbox to send a test email if you want; the sender filter still applies.
3. In GitHub **Settings → Secrets and variables → Actions**, create repository secrets `GMAIL_TOKEN_JSON` (the complete authorized-user JSON) and `OPENAI_API_KEY`. Set repository variable `TARGET_SENDER_EMAIL` to the exact sender email address. Do not put secrets in the email body.
4. In **Settings → Actions → General → Workflow permissions**, allow **Read and write permissions** and enable **Allow GitHub Actions to create and approve pull requests**. The workflow uses the built-in `GITHUB_TOKEN`; you do not need to create a personal access token. Repository or organization policy must allow these settings.
5. Email the Gmail account from `TARGET_SENDER_EMAIL`, with subject `updates` and a plain-text body containing a specific requested change. Open **Actions → personal-sync-agent → Run workflow**, or wait for the hourly schedule. Check the run logs and the new draft PR. Scheduled workflows run from the default branch and may be delayed by GitHub.

For local use, install `requirements.txt`, set `GMAIL_TOKEN_JSON`, `TARGET_SENDER_EMAIL`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, and `GITHUB_REPOSITORY=owner/repo` in your environment or a private `.env`, then run `python main.py` from a clean repository checkout with a push-enabled origin. Run tests with `python -m unittest discover -s tests -v`.

## Review and limitations

The LLM output is untrusted. The script accepts at most 10 UTF-8 files of 200 KB each, rejects hidden paths, workflow changes, and paths outside the checkout, and never auto-merges. It uses only plain-text email parts. The model receives the email text, **not repository files**; provide enough context in your message for complete-file replacements and inspect the entire diff. An invalid response leaves the email unread for retry. A failure after pushing but before marking an email read may produce another branch and draft PR on the next run; inspect existing PRs before merging duplicates. GitHub-hosted schedules are approximate, and your OpenAI usage may incur costs.
