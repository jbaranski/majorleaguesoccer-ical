import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  lastUpdated = '2025-11-27T16:05:46Z';
  teams = [
    'Atlanta United',
    'Austin FC',
    'CF Montreal',
    'Charlotte FC',
    'Chicago Fire FC',
    'Colorado Rapids',
    'Columbus Crew',
    'D.C. United',
    'FC Cincinnati',
    'FC Dallas',
    'Houston Dynamo FC',
    'Inter Miami CF',
    'LA Galaxy',
    'Los Angeles FC',
    'Minnesota United',
    'Nashville SC',
    'New England Revolution',
    'New York City FC',
    'New York Red Bulls',
    'Orlando City',
    'Philadelphia Union',
    'Portland Timbers',
    'Real Salt Lake',
    'San Diego FC',
    'San Jose Earthquakes',
    'Seattle Sounders FC',
    'Sporting Kansas City',
    'St. Louis City SC',
    'Toronto FC',
    'Vancouver Whitecaps FC'
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
