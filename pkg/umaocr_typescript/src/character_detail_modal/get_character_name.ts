import {ConfigResult, createWorker} from 'tesseract.js';

const worker = createWorker();

export default async (image: string): Promise<string> => {
    const ocr_character_name: string = await get_character_name_by_ocr(image)
    return ocr_character_name
}

async function get_character_name_by_ocr(image: string): Promise<string> {
    await worker.load();
    await worker.loadLanguage('jpn');
    await worker.initialize('jpn');
    try {
        const { data: { text } } = await worker.recognize(image);
        return text.replace(/\s+/g, "");
    } catch (err) {
        throw err;
    } finally {
        await worker.terminate();
    }
}