import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/deferred_intents_panel.dart';

void main() {
  testWidgets('Shows no deferred items message', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(body: DeferredIntentsPanel(items: [])),
      ),
    );

    expect(find.text('No deferred missions.'), findsOneWidget);
  });

  testWidgets('Shows deferred list and actions', (WidgetTester tester) async {
    final item = DeferredIntentItem(
      id: '1',
      description: 'Mission Later',
      scheduledFor: DateTime.now().add(const Duration(minutes: 10)),
      reason: 'Conflict',
    );

    bool runNowClicked = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: DeferredIntentsPanel(
            items: [item],
            onExecuteNow: (id) => runNowClicked = true,
          ),
        ),
      ),
    );

    expect(find.text('Mission Later'), findsOneWidget);
    expect(find.text('Run Now'), findsOneWidget);

    await tester.tap(find.text('Run Now'));
    expect(runNowClicked, isTrue);
  });
}
