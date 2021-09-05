import get_character_name from "./get_character_name";

describe('get_character_name', (): void => {
    test('OK', async () => {
        const character_name: string = await get_character_name('src/character_detail_modal/test.png');
        expect(character_name).toBe('ウオッカ');
    });
})
