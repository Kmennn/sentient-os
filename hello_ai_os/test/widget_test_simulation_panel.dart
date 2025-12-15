import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/simulation_insights_panel.dart';

void main() {
  testWidgets('Sim Stats Visualization', (WidgetTester tester) async {
    final stats = {"episodes": 500, "avg_reward": 120.5, "improvement": 15};

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: SimulationInsightsPanel(stats: stats)),
      ),
    );

    expect(find.text('500'), findsOneWidget);
    expect(find.text('+15%'), findsOneWidget);
    expect(
      find.byIcon(Icons.lock_outline),
      findsOneWidget,
    ); // Verify safety message
  });
}
