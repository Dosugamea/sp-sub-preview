import dataclasses
import functools
import re
import typing

from .directional import Directional
from .event import Event
from .line import Line
from .note import Note
from .slide import Slide
from .tap import Tap


class Score:
    """A model to represent sus with parsing"""

    def __init__(
        self,
        lines: list[Line] = [],
        events: list[Event] = [],
        notes: list[Note | Slide | Directional | Tap] = [],
    ) -> None:
        self.bpm_map: dict[str, float] = {}
        self.events: list[Event] = []
        self.notes: list[Note | Slide | Directional | Tap] = []

        if lines:
            for line in lines:
                for object in self.parse_line(line):
                    if isinstance(object, Event):
                        self.events.append(object)
                    elif isinstance(object, Note):
                        self.notes.append(object)

        if events:
            self.events += events

        if notes:
            self.notes += notes

        self.notes = sorted(set(self.notes), key=lambda note: note.bar)
        self.notes, self.note_events = self.parse_notes(
            self.notes, add_slide_intervals=True
        )

        self.events = sorted(
            self.events + self.note_events, key=lambda event: event.bar
        )
        self.events = self.parse_events(self.events)

    def parse_line(
        self, line: Line
    ) -> typing.Generator[Event | Tap | Slide | Directional, None, None]:
        # measure length
        if match := re.match(r"^(\d\d\d)02$", line.header):
            yield Event(bar=int(match.group(1)) + 0.0, bar_length=float(line.data))
        # bpm define
        elif match := re.match(r"^BPM(..)$", line.header):
            self.bpm_map[match.group(1)] = float(line.data)
        # bpm change
        elif match := re.match(r"^(\d\d\d)08$", line.header):
            for beat, data in self.parse_data(line.data):
                yield Event(bar=int(match.group(1)) + beat, bpm=self.bpm_map[data])
        # simple tap note
        elif match := re.match(r"^(\d\d\d)1(.)$", line.header):
            for beat, data in self.parse_data(line.data):
                yield Tap(
                    bar=int(match.group(1)) + beat,
                    lane=int(match.group(2), 36),
                    width=int(data[1], 36),
                    type=int(data[0], 36),
                )
        # slide note
        elif match := re.match(r"^(\d\d\d)3(.)(.)$", line.header):
            for beat, data in self.parse_data(line.data):
                yield Slide(
                    bar=int(match.group(1)) + beat,
                    lane=int(match.group(2), 36),
                    width=int(data[1], 36),
                    type=int(data[0], 36),
                    channel=int(match.group(3), 36),
                )
        # directional note
        elif match := re.match(r"^(\d\d\d)5(.)$", line.header):
            for beat, data in self.parse_data(line.data):
                yield Directional(
                    bar=int(match.group(1)) + beat,
                    lane=int(match.group(2), 36),
                    width=int(data[1], 36),
                    type=int(data[0], 36),
                )

    @functools.lru_cache()
    def get_time_event(self, bar: float) -> tuple[float, Event]:
        t = 0.0
        event = Event(bar=0.0, bpm=120.0, bar_length=4.0, sentence_length=4)

        for i in range(len(self.events)):
            event = event | self.events[i]
            if i + 1 == len(self.events) or self.events[i + 1].bar > bar + 1e-6:
                t += event.bar_length * 60 / event.bpm * (bar - event.bar)
                break
            else:
                t += (
                    event.bar_length
                    * 60
                    / event.bpm
                    * (self.events[i + 1].bar - event.bar)
                )

        return t, event

    def get_time(self, bar: float) -> float:
        return self.get_time_event(bar)[0]

    def get_event(self, bar: float) -> Event:
        return self.get_time_event(bar)[1]

    def get_time_delta(self, bar_from: float, bar_to: float) -> float:
        return self.get_time(bar_to) - self.get_time(bar_from)

    @functools.lru_cache()
    def get_bar_event(self, time: float) -> tuple[float, Event]:
        t = 0.0
        event = Event(bar=0.0, bpm=120.0, bar_length=4.0, sentence_length=4)

        for i in range(len(self.events)):
            event = event | self.events[i]
            if (
                i + 1 == len(self.events)
                or t
                + event.bar_length
                * 60
                / event.bpm
                * (self.events[i + 1].bar - event.bar)
                > time
            ):
                break
            else:
                t += (
                    event.bar_length
                    * 60
                    / event.bpm
                    * (self.events[i + 1].bar - event.bar)
                )

        bar = event.bar + (time - t) / (event.bar_length * 60 / event.bpm)

        return bar, event

    def get_bar(self, time: float) -> float:
        return self.get_bar_event(time)[0]

    @staticmethod
    def parse_events(sorted_events: list[Event]) -> list[Event]:
        events: list[Event] = []

        for event in sorted_events:
            if len(events) and "%e" % event.bar == "%e" % events[-1].bar:
                events[-1] |= event
            else:
                events.append(event)

        return events

    @staticmethod
    def parse_notes(
        sorted_notes: list[Note], add_slide_intervals=False
    ) -> tuple[list[Note], list[Event]]:
        notes: list[Note] = list(sorted_notes)
        note_events: list[Event] = []

        note_dict: dict[float, list[Note]] = {}
        for note in sorted_notes:
            if note.bar not in note_dict:
                note_dict[note.bar] = []
            note_dict[note.bar].append(note)

        for i, note in enumerate(sorted_notes):
            if not 0 <= note.lane - 2 < 12:
                notes.remove(note)
                note_events.append(
                    Event(
                        bar=note.bar,
                        text="SKILL"
                        if note.lane == 0
                        else "FEVER CHANCE!"
                        if note.type == 1
                        else "SUPER FEVER!!",
                    )
                )

        for i, note in enumerate(sorted_notes):
            if isinstance(note, Directional):
                directional = note

                for note in note_dict[directional.bar]:
                    if isinstance(note, Tap):
                        tap = note
                        if (
                            tap.bar == directional.bar
                            and tap.lane == directional.lane
                            and tap.width == directional.width
                        ):
                            notes.remove(tap)
                            note_dict[directional.bar].remove(tap)
                            directional.tap = tap
                            break

        for i, note in enumerate(sorted_notes):
            if isinstance(note, Slide):
                slide = note
                if slide.head is None:
                    slide.head = slide

                for note in note_dict[slide.bar]:
                    if isinstance(note, Tap):
                        tap = note
                        if (
                            tap.bar == slide.bar
                            and tap.lane == slide.lane
                            and tap.width == slide.width
                        ):
                            notes.remove(tap)
                            note_dict[slide.bar].remove(tap)
                            slide.tap = tap
                            break

                for note in note_dict[slide.bar]:
                    if isinstance(note, Directional):
                        directional = note
                        if (
                            directional.bar == slide.bar
                            and directional.lane == slide.lane
                            and directional.width == slide.width
                        ):
                            notes.remove(directional)
                            note_dict[slide.bar].remove(directional)
                            slide.directional = directional
                            if directional.tap is not None:
                                slide.tap = directional.tap
                            break

                if slide.type != 2:
                    for note in sorted_notes[i + 1 :]:
                        if isinstance(note, Slide):
                            if note.channel == slide.channel:
                                head = slide.head

                                interval = slide
                                if add_slide_intervals:
                                    bar = slide.bar + 1 / 8
                                    while bar + 1e-3 < note.bar:
                                        interval_next = Slide(
                                            bar,
                                            slide.lane,
                                            slide.width,
                                            0,
                                            slide.channel,
                                            head=head,
                                        )
                                        notes.append(interval_next)
                                        interval.next = interval_next
                                        interval = interval_next
                                        bar += 1 / 8

                                interval.next = note
                                note.head = slide.head
                                break

        return sorted(notes, key=lambda note: note.bar), note_events

    @staticmethod
    def parse_data(data: str) -> typing.Generator[tuple[float, str], None, None]:
        for i in range(0, len(data), 2):
            if data[i : i + 2] != "00":
                yield i / (len(data)), data[i : i + 2]

    def rebase(self, events: list[Event], offset=0.0) -> "Score":
        score = Score(events=events)

        for note_0 in self.notes:
            if isinstance(note_0, Tap):
                score.notes.append(
                    dataclasses.replace(
                        note_0,
                        bar=score.get_bar(self.get_time(note_0.bar) - offset),
                    )
                )
            elif isinstance(note_0, Directional):
                score.notes.append(
                    dataclasses.replace(
                        note_0,
                        bar=score.get_bar(self.get_time(note_0.bar) - offset),
                        tap=None,
                    )
                )
                if note_0.tap:
                    score.notes.append(
                        dataclasses.replace(
                            note_0.tap,
                            bar=score.get_bar(self.get_time(note_0.tap.bar) - offset),
                        )
                    )
            elif isinstance(note_0, Slide):
                score.notes.append(
                    dataclasses.replace(
                        note_0,
                        bar=score.get_bar(self.get_time(note_0.bar) - offset),
                        tap=None,
                        directional=None,
                        next=None,
                        head=None,
                    )
                )
                if note_0.tap is not None:
                    score.notes.append(
                        dataclasses.replace(
                            note_0.tap,
                            bar=score.get_bar(self.get_time(note_0.tap.bar) - offset),
                        )
                    )
                if note_0.directional is not None:
                    score.notes.append(
                        dataclasses.replace(
                            note_0.directional,
                            bar=score.get_bar(
                                self.get_time(note_0.directional.bar) - offset
                            ),
                            tap=None,
                        )
                    )
                    if (
                        note_0.directional.tap
                        and note_0.directional.tap is not note_0.tap
                    ):
                        score.notes.append(
                            dataclasses.replace(
                                note_0.directional.tap,
                                bar=score.get_bar(
                                    self.get_time(note_0.directional.tap.bar) - offset
                                ),
                            )
                        )

        score.notes.sort(key=lambda note: note.bar)
        score.notes, _ = score.parse_notes(score.notes)

        for note_event in self.note_events:
            score.note_events.append(
                dataclasses.replace(
                    note_event,
                    bar=score.get_bar(self.get_time(note_event.bar) - offset),
                )
            )

        score.events = sorted(
            score.events + score.note_events, key=lambda event: event.bar
        )
        score.events = score.parse_events(score.events)

        return score
