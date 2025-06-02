/**
 * Business Metrics Integration Test
 * Tests the new business metrics endpoints integration with the dashboard
 */

// Test the new business metrics endpoints
async function testBusinessMetricsEndpoints() {
    const baseUrl = 'http://localhost:5000';
    const endpoints = [
        '/api/qa_pass_rate',
        '/api/code_coverage', 
        '/api/sprint_velocity',
        '/api/completion_trend',
        '/api/qa_results',
        '/api/coverage_trend'
    ];

    console.log('🧪 Testing Business Metrics Endpoints Integration...\n');

    for (const endpoint of endpoints) {
        try {
            console.log(`Testing ${endpoint}...`);
            const response = await fetch(baseUrl + endpoint);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ ${endpoint} - Status: ${response.status}`);
                console.log(`   Status: ${data.status}`);
                console.log(`   Data keys: ${Object.keys(data.data || {}).join(', ')}`);
            } else {
                console.log(`❌ ${endpoint} - Status: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint} - Error: ${error.message}`);
        }
        console.log('');
    }
}

// Test dashboard integration
async function testDashboardIntegration() {
    console.log('\n📊 Testing Dashboard Integration...\n');
    
    try {
        // Test if dashboard loads the business metrics
        const qaPassRateResponse = await fetch('http://localhost:5000/api/qa_pass_rate');
        const qaData = await qaPassRateResponse.json();
        
        console.log('✅ QA Pass Rate Data Available:');
        console.log(`   Current Rate: ${qaData.data.current_rate}%`);
        console.log(`   Daily Trends: ${qaData.data.daily_trends?.length || 0} entries`);
        
        const sprintVelocityResponse = await fetch('http://localhost:5000/api/sprint_velocity');
        const velocityData = await sprintVelocityResponse.json();
        
        console.log('\n✅ Sprint Velocity Data Available:');
        console.log(`   Current Velocity: ${velocityData.data.current_velocity}`);
        console.log(`   Average Velocity: ${velocityData.data.average_velocity}`);
        console.log(`   Sprint History: ${velocityData.data.sprint_history?.length || 0} entries`);
        
        const codeCoverageResponse = await fetch('http://localhost:5000/api/code_coverage');
        const coverageData = await codeCoverageResponse.json();
        
        console.log('\n✅ Code Coverage Data Available:');
        console.log(`   Overall Coverage: ${coverageData.data.overall_coverage}%`);
        console.log(`   Module Breakdown: ${Object.keys(coverageData.data.module_breakdown || {}).length} modules`);
        
    } catch (error) {
        console.log(`❌ Dashboard Integration Error: ${error.message}`);
    }
}

// Main test execution
async function runTests() {
    console.log('🚀 Business Metrics Integration Test Suite\n');
    console.log('='.repeat(50));
    
    await testBusinessMetricsEndpoints();
    await testDashboardIntegration();
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ Business Metrics Integration Tests Complete!');
    console.log('\nThe dashboard should now display:');
    console.log('• Real-time QA Pass Rate with trends');
    console.log('• Code Coverage metrics with module breakdown');
    console.log('• Sprint Velocity with historical data');
    console.log('• Completion trends over time');
    console.log('• QA Results with detailed test breakdowns');
    console.log('• Coverage trends with visual charts');
}

// Run tests when page loads
if (typeof window !== 'undefined') {
    window.addEventListener('load', runTests);
} else {
    // Node.js environment
    runTests();
}
