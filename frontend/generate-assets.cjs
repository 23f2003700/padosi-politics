const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const sourceIcon = './pad.png';
const androidResDir = './android/app/src/main/res';

// Android icon sizes
const iconSizes = [
  { folder: 'mipmap-mdpi', size: 48 },
  { folder: 'mipmap-hdpi', size: 72 },
  { folder: 'mipmap-xhdpi', size: 96 },
  { folder: 'mipmap-xxhdpi', size: 144 },
  { folder: 'mipmap-xxxhdpi', size: 192 },
];

// Splash screen sizes
const splashSizes = [
  { folder: 'drawable', size: 480 },
  { folder: 'drawable-land-mdpi', width: 480, height: 320 },
  { folder: 'drawable-land-hdpi', width: 800, height: 480 },
  { folder: 'drawable-land-xhdpi', width: 1280, height: 720 },
  { folder: 'drawable-land-xxhdpi', width: 1600, height: 960 },
  { folder: 'drawable-land-xxxhdpi', width: 1920, height: 1280 },
  { folder: 'drawable-port-mdpi', width: 320, height: 480 },
  { folder: 'drawable-port-hdpi', width: 480, height: 800 },
  { folder: 'drawable-port-xhdpi', width: 720, height: 1280 },
  { folder: 'drawable-port-xxhdpi', width: 960, height: 1600 },
  { folder: 'drawable-port-xxxhdpi', width: 1280, height: 1920 },
];

async function generateIcons() {
  console.log('🎨 Generating Android icons...');
  
  for (const { folder, size } of iconSizes) {
    const outputDir = path.join(androidResDir, folder);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // Regular icon
    await sharp(sourceIcon)
      .resize(size, size)
      .png()
      .toFile(path.join(outputDir, 'ic_launcher.png'));
    
    // Round icon
    await sharp(sourceIcon)
      .resize(size, size)
      .png()
      .toFile(path.join(outputDir, 'ic_launcher_round.png'));
    
    // Foreground for adaptive icon
    await sharp(sourceIcon)
      .resize(Math.floor(size * 1.5), Math.floor(size * 1.5))
      .png()
      .toFile(path.join(outputDir, 'ic_launcher_foreground.png'));
    
    console.log(`  ✅ ${folder}: ${size}x${size}`);
  }
}

async function generateSplash() {
  console.log('🌊 Generating splash screens...');
  
  // Brand color
  const brandColor = '#2563eb'; // Blue
  
  for (const splash of splashSizes) {
    const outputDir = path.join(androidResDir, splash.folder);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }
    
    const width = splash.width || splash.size;
    const height = splash.height || splash.size;
    const iconSize = Math.min(width, height) * 0.4;
    
    // Create splash with colored background and centered icon
    const background = await sharp({
      create: {
        width: width,
        height: height,
        channels: 4,
        background: { r: 37, g: 99, b: 235, alpha: 1 } // #2563eb
      }
    }).png().toBuffer();
    
    const icon = await sharp(sourceIcon)
      .resize(Math.floor(iconSize), Math.floor(iconSize))
      .png()
      .toBuffer();
    
    await sharp(background)
      .composite([{
        input: icon,
        gravity: 'center'
      }])
      .png()
      .toFile(path.join(outputDir, 'splash.png'));
    
    console.log(`  ✅ ${splash.folder}: ${width}x${height}`);
  }
}

async function main() {
  try {
    await generateIcons();
    await generateSplash();
    console.log('\n✨ All assets generated successfully!');
  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

main();
