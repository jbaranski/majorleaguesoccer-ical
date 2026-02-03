import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  readonly lastUpdated = '2026-02-03T01:57:46Z';
  readonly teams = [
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
  ].map((name) => ({
    name,
    url: `https://raw.githubusercontent.com/jbaranski/majorleaguesoccer-ical/refs/heads/main/calendars/${name.replaceAll('.', '').replaceAll(' ', '').toLowerCase()}.ics`
  }));
  copyToClipboardText = signal(Array(this.teams.length).fill('Copy to clipboard'));

  onCopyToClipboard(event: Event, teamUrl: string, i: number) {
    navigator.clipboard.writeText(teamUrl);
    this.copyToClipboardText.update((values: string[]) => {
      const newValues = [...values];
      newValues[i] = 'Copied!';
      return newValues;
    });
    setTimeout(() => {
      this.copyToClipboardText.update((values: string[]) => {
        const newValues = [...values];
        newValues[i] = 'Copy to clipboard';
        return newValues;
      });
    }, 2500);
  }
}
