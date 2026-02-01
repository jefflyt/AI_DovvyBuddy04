import { test, expect } from '@playwright/test';

test.describe('Landing Page Chat Preview', () => {
    test('should navigate to /chat with prompt when clicking "Try this question"', async ({ page }) => {
        // Navigate to landing page
        await page.goto('/');

        // Wait for ChatPreview to load
        await page.waitForSelector('text=Try this question');

        // Click the "Try this question" button
        await page.click('text=Try this question');

        // Wait for navigation
        await page.waitForURL(/\/chat\?prompt=.+/);

        // Verify URL contains prompt parameter
        const url = page.url();
        expect(url).toContain('/chat?prompt=');
        expect(url).toContain('Advanced%20Open%20Water');
    });

    test('should switch tabs and navigate with different prompts', async ({ page }) => {
        await page.goto('/');

        // Click on "Dive Site Match" tab
        await page.click('text=Dive Site Match');

        // Wait for tab content to update
        await page.waitForSelector('text=manta rays');

        // Click "Try this question"
        await page.click('text=Try this question');

        // Wait for navigation
        await page.waitForURL(/\/chat\?prompt=.+/);

        // Verify URL contains the dive site prompt
        const url = page.url();
        expect(url).toContain('manta%20rays');
    });
});
