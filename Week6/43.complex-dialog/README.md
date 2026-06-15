# Complex Dialog Sample

This sample creates a complex conversation with dialogs.

This copy is based on Microsoft's `43.complex-dialog` sample (BotBuilder-Samples)
and has been extended across two assignments:

- **Week 5** added a "capabilities" command/welcome message and reworked the idle
  message handler so out-of-scope input no longer gets swallowed as the start of
  the name/age dialog.
- **Week 6** integrated Google's **Gemini API** as a cloud AI-as-a-service: any
  idle input that isn't a recognized command (`start`/`restart`/`begin`,
  `help`/`capabilities`) is now answered by Gemini instead of a static message.

## Bot Capabilities

- Collects the user's name and age via a multi-step dialog.
- If the user is 25 or older, lets them pick companies to review.
- Remembers answers/choices for the duration of the conversation.
- Responds to `help` / `capabilities` / `what can you do` with a summary of the
  above.
- Answers any other message (questions, phrases, or otherwise unrecognized
  input) using Gemini (see `helpers/ai_helper.py`).

## To try this sample

- Clone the repository
    ```bash
    git clone https://github.com/manishfsb/AI4HCI/Week6.git
    ```
- In a terminal, navigate to the `Week6/43.complex-dialog` folder
- Activate your desired virtual environment
- Create a `.env` file in the repository root containing your Gemini API key:
  ```
  GEMINI_API_KEY=your-gemini-api-key-here
  ```
  (Get a free key from [Google AI Studio](https://aistudio.google.com). Without
  this, the bot still runs, but falls back to a "not configured" message for
  any input Gemini would otherwise answer.)
- In the terminal, type `pip install -r requirements.txt`
- Run your bot with `python app.py`

## Testing the bot using Bot Framework Emulator

[Bot Framework Emulator](https://github.com/microsoft/botframework-emulator) is a desktop application that allows bot developers to test and debug their bots on localhost or running remotely through a tunnel.

- Install the latest Bot Framework Emulator from [here](https://github.com/Microsoft/BotFramework-Emulator/releases)

### Connect to the bot using Bot Framework Emulator

- Launch Bot Framework Emulator
- File -> Open Bot
- Enter a Bot URL of `http://localhost:3978/api/messages`

## Deploy the bot to Azure

To learn more about deploying a bot to Azure, see [Deploy your bot to Azure](https://aka.ms/azuredeployment) for a complete list of deployment instructions.

## Further reading

- [Bot Framework Documentation](https://docs.botframework.com)
- [Bot Basics](https://docs.microsoft.com/azure/bot-service/bot-builder-basics?view=azure-bot-service-4.0)
- [Activity processing](https://docs.microsoft.com/en-us/azure/bot-service/bot-builder-concept-activity-processing?view=azure-bot-service-4.0)
- [Azure Bot Service Introduction](https://docs.microsoft.com/azure/bot-service/bot-service-overview-introduction?view=azure-bot-service-4.0)
- [Azure Bot Service Documentation](https://docs.microsoft.com/azure/bot-service/?view=azure-bot-service-4.0)
- [Azure CLI](https://docs.microsoft.com/cli/azure/?view=azure-cli-latest)
- [Azure Portal](https://portal.azure.com)
- [Channels and Bot Connector Service](https://docs.microsoft.com/en-us/azure/bot-service/bot-concepts?view=azure-bot-service-4.0)
