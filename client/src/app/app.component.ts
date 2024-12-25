import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  imports: [],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  teams = [
    'Atlanta United FC',
    'Austin',
    'CF Montreal',
    'Charlotte',
    'Chicago Fire',
    'Colorado Rapids',
    'Columbus Crew',
    'DC United',
    'FC Cincinnati',
    'FC Dallas',
    'Houston Dynamo',
    'Inter Miami',
    'Los Angeles FC',
    'Los Angeles Galaxy',
    'Minnesota United FC',
    'Nashville SC',
    'New England Revolution',
    'New York City FC',
    'New York Red Bulls',
    'Orlando City SC',
    'Philadelphia Union',
    'Portland Timbers',
    'Real Salt Lake',
    'San Diego',
    'San Jose Earthquakes',
    'Seattle Sounders',
    'Sporting Kansas City',
    'St. Louis City',
    'Toronto FC',
    'Vancouver Whitecaps'
  ];
  copyToClipboardText = Array(30).fill('Copy to clipboard');

  getCalendarUrl(team: string): string {
    return `https://raw.githubusercontent.com/jbaranski/majorleaguesoccer-ical/refs/heads/main/calendars/${team.replaceAll('.', '').replaceAll(' ', '').toLowerCase()}.ics`;
  }

  onCopyToClipboard(event: Event, team: string, i: number) {
    navigator.clipboard.writeText(this.getCalendarUrl(team));
    this.copyToClipboardText[i] = 'Copied!';
    setTimeout(() => {
      this.copyToClipboardText[i] = 'Copy to clipboard';
    }, 2500);
  }
}
