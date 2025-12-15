import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/mission_queue_panel.dart';

void main() {
  testWidgets('Mission Queue Panel renders sections', (
    WidgetTester tester,
  ) async {
    final missions = [
      MissionEntry(id: "CleanKitchen", priority: "BACKGROUND", isPaused: true),
      MissionEntry(id: "EmergencyStop", priority: "CRITICAL", isActive: true),
      MissionEntry(id: "TidyUp", priority: "SYSTEM"),
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: MissionQueuePanel(
            missions: missions,
            onAbort: (_) {},
            onResume: (_) {},
          ),
        ),
      ),
    );

    expect(find.text("Active Execution"), findsOneWidget);
    expect(find.text("EmergencyStop"), findsOneWidget);

    expect(find.text("Paused / Preempted"), findsOneWidget);
    expect(find.text("CleanKitchen"), findsOneWidget);

    expect(find.text("Pending Queue"), findsOneWidget);
    expect(find.text("TidyUp"), findsOneWidget);
  });
}
