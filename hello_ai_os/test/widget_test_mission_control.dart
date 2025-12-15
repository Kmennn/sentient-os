import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/mission_control_center.dart';

void main() {
  testWidgets('Mission Control Creation', (WidgetTester tester) async {
    bool started = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionControlCenter(
            onStartMission: (n, a) => started = true,
            onAbort: () {},
            status: "IDLE",
          ),
        ),
      ),
    );

    // Check form
    expect(find.text('Mission Name'), findsOneWidget);
    expect(find.text('Allow: Pick'), findsOneWidget);

    // Start
    await tester.tap(find.text('SIGN CONTRACT & EXECUTE'));
    expect(started, isTrue);
  });

  testWidgets('Abort Button in Execution', (WidgetTester tester) async {
    bool aborted = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionControlCenter(
            onStartMission: (_, __) {},
            onAbort: () => aborted = true,
            status: "EXECUTING",
          ),
        ),
      ),
    );

    expect(find.text('ABORT MISSION (SAFETY OVERRIDE)'), findsOneWidget);
    await tester.tap(find.text('ABORT MISSION (SAFETY OVERRIDE)'));
    expect(aborted, isTrue);
  });
}
