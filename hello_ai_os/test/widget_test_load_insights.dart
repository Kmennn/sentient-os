import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/load_insights_page.dart';

void main() {
  testWidgets('LoadInsightsPage displays observations', (
    WidgetTester tester,
  ) async {
    final obs = ["Monday is busy."];

    await tester.pumpWidget(
      MaterialApp(home: LoadInsightsPage(observations: obs)),
    );

    expect(find.text("Monday is busy."), findsOneWidget);
    expect(find.byIcon(Icons.bolt), findsOneWidget);
  });

  testWidgets('LoadInsightsPage shows warning for high load', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: LoadInsightsPage(observations: [], hasHighLoad: true),
      ),
    );

    expect(
      find.text("High load periods detected. Consider recovery."),
      findsOneWidget,
    );
    expect(find.byIcon(Icons.warning), findsOneWidget);
  });
}
