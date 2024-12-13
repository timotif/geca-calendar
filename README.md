# GECA Calendar
This is a Python dockerized webapp that handles a subscription calendar for [Geneva Camerata](https://genevacamerata.com/en) events

## Features

- Fetch calendar data from Notion
- Subscribe to calendar
- Save calendars locally in ICS format

## Getting Started

### Prerequisites

- Python 3.x
- Notion API token
- *(For local mode)* Virtual environment (venv)
- .env file (see env_template)

### Create Notion integration token
- Settings and members
- Connections (left menu, second last) => Develop or manage integration (second last option, below the connection list)
    + Type: Internal
    + Associated workspace: the season workspace
    + Name: Whatever you like! Let's say <yourname_integration>
    + Click Submit
- In the integration page click on Capabilities and uncheck the Update and Insert => Save changes
- Secret => Show => Copy
Share a page with the integration
- Open the page (Calendar in our case)
- Click on the '...' on the top right corner
- Click on Add connection
- In that list the Integration you created previously should show up: if it doesn't you might have connected the integration to the workspace and should repeat the first steps
- Select the integration and click Confirm
Retrieve the calendar id
- The page address looks something like this: https://word-generated-code.notion.site/PAGE_TITLE-alphanumeric_code
- Open the calendar and the address will look something like this: https://word-generated-code.notion.site/**alphanumeric-id**?v=alphanumeric-code
- The alphanumeric-id is the calendar id


### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/timotif/geca-calendar.git
   cd geca-calendar
   ```

## Usage
### Webapp Mode
```bash
make build
make run
```
The app will be available at http://localhost:8001 (can be changed in the Makefile PORT variable)

### Hosting
- You can host the app on a server and expose the port 8001

#### Subscribing to a Calendar
- *iCal*
  1. Click on **New Calendar** -> **Add subscribed calendar**
  2. Paste the calendar link and click **Subscribe**

- *Google and Android*
For detailed instructions on adding a calendar to Google Calendar, refer to [this guide](https://www.ohmancorp.com/refhowto-androidaddinternetcalendar.asp).

### Stop the app 
```bash
make stop
```
### Clean up
```bash
make fclean
```

### Local Calendar Save Mode

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r geca_calendar/requirements.txt
   ```

2. **Run the update script**:
   ```bash
   ./update_calendar.sh
   ```

The calendar file in ICS format will be saved in the root folder.

## Help

Check the Makefile for more commands:
```bash
make help
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or support, please contact [timotif@gmail.com](mailto:timotif@gmail.com).

---

**Note**: This project is intended for non-commercial use only. Please refer to the license for more details.