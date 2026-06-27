import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

const BASE =
  'https://raw.githubusercontent.com/jbaranski/majorleaguesoccer-ical/refs/heads/main/calendars/international';

@Component({
  selector: 'app-international',
  imports: [CommonModule, RouterLink],
  templateUrl: './international.component.html'
})
export class InternationalComponent {
  readonly lastUpdated = '2026-06-27T18:48:13Z';
  readonly competitions = [
    { name: 'World Cup', urlName: 'worldcup' },
    { name: 'Gold Cup', urlName: 'goldcup' },
    { name: 'Copa América', urlName: 'copamerica' },
    { name: 'CONCACAF Nations League', urlName: 'concacafnationsleague' }
  ].map(({ name, urlName }) => ({ name, url: `${BASE}/${urlName}.ics` }));

  readonly teams = [
    { name: 'Algeria', urlName: 'algeria' },
    { name: 'Argentina', urlName: 'argentina' },
    { name: 'Australia', urlName: 'australia' },
    { name: 'Austria', urlName: 'austria' },
    { name: 'Belgium', urlName: 'belgium' },
    { name: 'Bosnia and Herzegovina', urlName: 'bosniaandherzegovina' },
    { name: 'Brazil', urlName: 'brazil' },
    { name: 'Canada', urlName: 'canada' },
    { name: 'Cape Verde', urlName: 'capeverde' },
    { name: 'Colombia', urlName: 'colombia' },
    { name: 'Croatia', urlName: 'croatia' },
    { name: 'Curacao', urlName: 'curacao' },
    { name: 'Czech Republic', urlName: 'czechrepublic' },
    { name: 'DR Congo', urlName: 'drcongo' },
    { name: 'Ecuador', urlName: 'ecuador' },
    { name: 'Egypt', urlName: 'egypt' },
    { name: 'England', urlName: 'england' },
    { name: 'France', urlName: 'france' },
    { name: 'Germany', urlName: 'germany' },
    { name: 'Ghana', urlName: 'ghana' },
    { name: 'Haiti', urlName: 'haiti' },
    { name: 'Iran', urlName: 'iran' },
    { name: 'Iraq', urlName: 'iraq' },
    { name: 'Ivory Coast', urlName: 'ivorycoast' },
    { name: 'Japan', urlName: 'japan' },
    { name: 'Jordan', urlName: 'jordan' },
    { name: 'Mexico', urlName: 'mexico' },
    { name: 'Morocco', urlName: 'morocco' },
    { name: 'Netherlands', urlName: 'netherlands' },
    { name: 'New Zealand', urlName: 'newzealand' },
    { name: 'Norway', urlName: 'norway' },
    { name: 'Panama', urlName: 'panama' },
    { name: 'Paraguay', urlName: 'paraguay' },
    { name: 'Portugal', urlName: 'portugal' },
    { name: 'Qatar', urlName: 'qatar' },
    { name: 'Saudi Arabia', urlName: 'saudiarabia' },
    { name: 'Scotland', urlName: 'scotland' },
    { name: 'Senegal', urlName: 'senegal' },
    { name: 'South Africa', urlName: 'southafrica' },
    { name: 'South Korea', urlName: 'southkorea' },
    { name: 'Spain', urlName: 'spain' },
    { name: 'Sweden', urlName: 'sweden' },
    { name: 'Switzerland', urlName: 'switzerland' },
    { name: 'Tunisia', urlName: 'tunisia' },
    { name: 'Turkiye', urlName: 'turkiye' },
    { name: 'United States', urlName: 'unitedstates' },
    { name: 'Uruguay', urlName: 'uruguay' },
    { name: 'Uzbekistan', urlName: 'uzbekistan' }
  ].map(({ name, urlName }) => ({ name, url: `${BASE}/countries/${urlName}.ics` }));

  competitionCopyText = signal(Array(this.competitions.length).fill('Copy to clipboard'));
  teamCopyText = signal(Array(this.teams.length).fill('Copy to clipboard'));

  onCopyCompetition(event: Event, url: string, i: number) {
    this.copyAndReset(url, i, this.competitionCopyText);
  }

  onCopyTeam(event: Event, url: string, i: number) {
    this.copyAndReset(url, i, this.teamCopyText);
  }

  private copyAndReset(url: string, i: number, sig: ReturnType<typeof signal<string[]>>) {
    navigator.clipboard.writeText(url);
    sig.update((values) => {
      const v = [...values];
      v[i] = 'Copied!';
      return v;
    });
    setTimeout(() => {
      sig.update((values) => {
        const v = [...values];
        v[i] = 'Copy to clipboard';
        return v;
      });
    }, 2500);
  }
}
