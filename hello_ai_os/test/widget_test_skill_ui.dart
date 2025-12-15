import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/teach_mode_panel.dart';
import 'package:hello_ai_os/ui/skill_library_page.dart';

void main() {
  testWidgets('Teach Mode Buttons', (WidgetTester tester) async {
    bool recording = false;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: TeachModePanel(
            isRecording: false,
            onRecordToggle: (val) => recording = val,
          ),
        ),
      ),
    );

    expect(find.text('Start Recording'), findsOneWidget);
    await tester.tap(find.text('Start Recording'));
    expect(recording, true);
  });

  testWidgets('Skill Library List', (WidgetTester tester) async {
    String? replayed;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: SkillLibraryPage(
            skills: ['PickCup', 'Wave'],
            onReplay: (s) => replayed = s,
          ),
        ),
      ),
    );

    expect(find.text('PickCup'), findsOneWidget);
    expect(find.text('Wave'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.play_arrow).first);
    expect(replayed, 'PickCup');
  });
}
