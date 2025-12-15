import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/mission_trust_panel.dart';

void main() {
  testWidgets('Trust Panel High Trust', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionTrustPanel(
            trustScore: 0.9,
            onResume: () {},
            onAbort: () {},
          ),
        ),
      ),
    );

    expect(find.text('Tier: HIGH'), findsOneWidget);
    expect(find.byType(LinearProgressIndicator), findsOneWidget);
    expect(find.text('Active Mission Found! System restarted.'), findsNothing);
  });

  testWidgets('Trust Panel Low Trust', (WidgetTester tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionTrustPanel(
            trustScore: 0.3,
            onResume: () {},
            onAbort: () {},
          ),
        ),
      ),
    );

    expect(find.text('Tier: LOW (Strict Supervision)'), findsOneWidget);
  });

  testWidgets('Recovery Mode', (WidgetTester tester) async {
    bool resumed = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionTrustPanel(
            trustScore: 0.8,
            isRecoveryAvailable: true,
            onResume: () => resumed = true,
            onAbort: () {},
          ),
        ),
      ),
    );

    expect(
      find.text('Active Mission Found! System restarted.'),
      findsOneWidget,
    );
    await tester.tap(find.text('RESUME MISSION'));
    expect(resumed, isTrue);
  });
}
