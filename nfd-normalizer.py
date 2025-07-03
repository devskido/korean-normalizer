#!/usr/bin/env python3
"""
Universal NFD to NFC Filename Normalizer
=======================================

This script recursively normalizes filenames from NFD (Normalization Form Decomposed) 
to NFC (Normalization Form Composed) format for all languages and platforms.

Supports:
- All Unicode characters (Korean, Japanese, Chinese, European accents, etc.)
- All operating systems (Mac, Windows, Linux)
- Safe handling of edge cases and conflicts
- Backup and restore functionality

Usage:
    python3 normalize_filenames.py [directory] [options]
    
Options:
    --dry-run, -n     Preview changes without making them
    --all-files       Process all files, not just those with non-ASCII characters
    --backup          Create backup mapping file for restoration
    --force           Force normalization even if target filename exists
    --quiet, -q       Suppress detailed output
    --stats-only      Show statistics without making changes
    
If no directory is specified, the current directory is used.
"""

import os
import sys
import unicodedata
import json
import argparse
from datetime import datetime
from pathlib import Path
import hashlib
import shutil

class UniversalNFCNormalizer:
    def __init__(self, directory='.', dry_run=False, all_files=False, 
                 backup=False, force=False, quiet=False, stats_only=False):
        self.directory = Path(directory).resolve()
        self.dry_run = dry_run or stats_only
        self.all_files = all_files
        self.backup = backup
        self.force = force
        self.quiet = quiet
        self.stats_only = stats_only
        
        self.stats = {
            'files_scanned': 0,
            'dirs_scanned': 0,
            'non_ascii_files': 0,
            'non_ascii_dirs': 0,
            'needs_normalization': 0,
            'renamed_success': 0,
            'renamed_failed': 0,
            'skipped_exists': 0,
            'by_language': {}
        }
        
        self.backup_data = []
        self.items_to_rename = []
        
    def detect_character_types(self, text):
        """Detect which language/script types are present in the text."""
        types = set()
        
        for char in text:
            code = ord(char)
            
            # Korean
            if 0xAC00 <= code <= 0xD7AF or 0x1100 <= code <= 0x11FF or 0x3130 <= code <= 0x318F:
                types.add('Korean')
            # Japanese Hiragana/Katakana
            elif 0x3040 <= code <= 0x309F or 0x30A0 <= code <= 0x30FF:
                types.add('Japanese')
            # Chinese (CJK Unified Ideographs)
            elif 0x4E00 <= code <= 0x9FFF:
                types.add('Chinese/CJK')
            # Latin with diacritics
            elif 0x00C0 <= code <= 0x024F:
                types.add('Latin Extended')
            # Cyrillic
            elif 0x0400 <= code <= 0x04FF:
                types.add('Cyrillic')
            # Arabic
            elif 0x0600 <= code <= 0x06FF:
                types.add('Arabic')
            # Thai
            elif 0x0E00 <= code <= 0x0E7F:
                types.add('Thai')
            # Other non-ASCII
            elif code > 127:
                types.add('Other Unicode')
                
        return types
    
    def analyze_normalization(self, text):
        """Comprehensive analysis of text normalization needs."""
        nfc = unicodedata.normalize('NFC', text)
        nfd = unicodedata.normalize('NFD', text)
        nfkc = unicodedata.normalize('NFKC', text)
        nfkd = unicodedata.normalize('NFKD', text)
        
        char_types = self.detect_character_types(text)
        
        # Check if text has any non-ASCII characters
        has_non_ascii = any(ord(c) > 127 for c in text)
        
        # Determine if normalization is needed
        needs_normalization = text != nfc if not self.all_files else (
            has_non_ascii and text != nfc
        )
        
        return {
            'original': text,
            'nfc': nfc,
            'nfd': nfd,
            'nfkc': nfkc,
            'nfkd': nfkd,
            'is_nfc': text == nfc,
            'is_nfd': text == nfd,
            'has_non_ascii': has_non_ascii,
            'needs_normalization': needs_normalization,
            'char_types': char_types,
            'original_len': len(text),
            'nfc_len': len(nfc),
            'byte_size_change': len(nfc.encode('utf-8')) - len(text.encode('utf-8'))
        }
    
    def safe_rename(self, old_path, new_path):
        """Safely rename file/directory with conflict handling."""
        if new_path.exists() and not self.force:
            # Generate unique name if target exists
            base = new_path.stem
            suffix = new_path.suffix
            parent = new_path.parent
            counter = 1
            
            while new_path.exists():
                new_name = f"{base}_nfc{counter}{suffix}"
                new_path = parent / new_name
                counter += 1
                
            if not self.quiet:
                print(f"   ⚠️  Target exists, using: {new_path.name}")
            self.stats['skipped_exists'] += 1
        
        try:
            if self.backup:
                # Store backup information
                self.backup_data.append({
                    'original_path': str(old_path),
                    'new_path': str(new_path),
                    'timestamp': datetime.now().isoformat(),
                    'file_hash': self.get_file_hash(old_path) if old_path.is_file() else None
                })
            
            old_path.rename(new_path)
            self.stats['renamed_success'] += 1
            return True
            
        except Exception as e:
            if not self.quiet:
                print(f"   ❌ Failed: {e}")
            self.stats['renamed_failed'] += 1
            return False
    
    def get_file_hash(self, filepath):
        """Calculate file hash for backup verification."""
        if not filepath.is_file():
            return None
            
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except:
            return None
    
    def collect_items(self, directory=None):
        """Recursively collect all items that need processing."""
        if directory is None:
            directory = self.directory
            
        try:
            items = list(directory.iterdir())
            # Sort to process files before directories
            items.sort(key=lambda x: (x.is_dir(), x.name))
        except (OSError, PermissionError) as e:
            if not self.quiet:
                print(f"❌ Cannot access directory: {directory}: {e}")
            return
        
        for item_path in items:
            try:
                item_name = item_path.name
                analysis = self.analyze_normalization(item_name)
                
                if item_path.is_file():
                    self.stats['files_scanned'] += 1
                    
                    if analysis['has_non_ascii']:
                        self.stats['non_ascii_files'] += 1
                        
                        # Update language statistics
                        for lang in analysis['char_types']:
                            self.stats['by_language'][lang] = self.stats['by_language'].get(lang, 0) + 1
                        
                        if not self.quiet and not self.stats_only:
                            print(f"\n📄 File: {item_name}")
                            print(f"   Character types: {', '.join(analysis['char_types'])}")
                            print(f"   Needs normalization: {analysis['needs_normalization']}")
                        
                        if analysis['needs_normalization']:
                            self.stats['needs_normalization'] += 1
                            self.items_to_rename.append({
                                'path': item_path,
                                'old_name': item_name,
                                'new_name': analysis['nfc'],
                                'type': 'file',
                                'analysis': analysis
                            })
                            
                            if not self.quiet and not self.stats_only:
                                print(f"   🔄 Will normalize to: {analysis['nfc']}")
                
                elif item_path.is_dir():
                    self.stats['dirs_scanned'] += 1
                    
                    if analysis['has_non_ascii']:
                        self.stats['non_ascii_dirs'] += 1
                        
                        if not self.quiet and not self.stats_only:
                            print(f"\n📁 Directory: {item_name}")
                            print(f"   Character types: {', '.join(analysis['char_types'])}")
                            print(f"   Needs normalization: {analysis['needs_normalization']}")
                        
                        if analysis['needs_normalization']:
                            self.stats['needs_normalization'] += 1
                            self.items_to_rename.append({
                                'path': item_path,
                                'old_name': item_name,
                                'new_name': analysis['nfc'],
                                'type': 'directory',
                                'analysis': analysis
                            })
                            
                            if not self.quiet and not self.stats_only:
                                print(f"   🔄 Will normalize to: {analysis['nfc']}")
                    
                    # Recursively process subdirectory
                    self.collect_items(item_path)
                    
            except Exception as e:
                if not self.quiet:
                    print(f"⚠️  Cannot process {item_path}: {e}")
    
    def show_statistics(self):
        """Display comprehensive statistics."""
        print("\n📊 Scan Statistics:")
        print(f"   Total files scanned: {self.stats['files_scanned']}")
        print(f"   Total directories scanned: {self.stats['dirs_scanned']}")
        print(f"   Files with non-ASCII characters: {self.stats['non_ascii_files']}")
        print(f"   Directories with non-ASCII characters: {self.stats['non_ascii_dirs']}")
        print(f"   Items needing normalization: {self.stats['needs_normalization']}")
        
        if self.stats['by_language']:
            print("\n🌍 Character Types Found:")
            for lang, count in sorted(self.stats['by_language'].items()):
                print(f"   {lang}: {count} items")
        
        if not self.stats_only and not self.dry_run:
            print(f"\n✅ Normalization Results:")
            print(f"   Successfully renamed: {self.stats['renamed_success']}")
            print(f"   Failed to rename: {self.stats['renamed_failed']}")
            print(f"   Skipped (name conflicts): {self.stats['skipped_exists']}")
    
    def save_backup_mapping(self):
        """Save backup mapping for potential restoration."""
        if not self.backup or not self.backup_data:
            return
            
        backup_file = self.directory / f"nfc_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'directory': str(self.directory),
                    'mappings': self.backup_data,
                    'stats': self.stats
                }, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 Backup saved to: {backup_file}")
        except Exception as e:
            print(f"\n❌ Failed to save backup: {e}")
    
    def run(self):
        """Main execution method."""
        print(f"🔍 Scanning directory: {self.directory}")
        print("=" * 60)
        
        # Collect all items
        self.collect_items()
        
        # Show statistics
        self.show_statistics()
        
        if self.stats_only:
            return
        
        if not self.items_to_rename:
            print("\n✅ All filenames are already properly normalized!")
            return
        
        if self.dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made")
            return
        
        # Separate files and directories
        files_to_rename = [item for item in self.items_to_rename if item['type'] == 'file']
        dirs_to_rename = [item for item in self.items_to_rename if item['type'] == 'directory']
        
        # Sort directories by depth (deepest first)
        dirs_to_rename.sort(key=lambda x: len(x['path'].parts), reverse=True)
        
        print(f"\n🚀 Starting normalization...")
        
        # Rename files first
        if files_to_rename:
            print(f"\n📄 Processing {len(files_to_rename)} files...")
            for item in files_to_rename:
                old_path = item['path']
                new_path = old_path.parent / item['new_name']
                
                if not self.quiet:
                    print(f"   {item['old_name']} → {item['new_name']}")
                
                self.safe_rename(old_path, new_path)
        
        # Rename directories
        if dirs_to_rename:
            print(f"\n📁 Processing {len(dirs_to_rename)} directories...")
            for item in dirs_to_rename:
                old_path = item['path']
                new_path = old_path.parent / item['new_name']
                
                if not self.quiet:
                    print(f"   {item['old_name']} → {item['new_name']}")
                
                self.safe_rename(old_path, new_path)
        
        # Save backup if requested
        self.save_backup_mapping()
        
        print(f"\n🎉 Normalization complete!")


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Universal NFD to NFC Filename Normalizer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                     # Normalize current directory
  %(prog)s /path/to/dir        # Normalize specific directory
  %(prog)s -n                  # Dry run (preview changes)
  %(prog)s --all-files         # Process all files including ASCII-only
  %(prog)s --backup            # Create restoration backup
  %(prog)s --stats-only        # Show statistics without changes
        """
    )
    
    parser.add_argument('directory', nargs='?', default='.',
                      help='Directory to process (default: current directory)')
    parser.add_argument('-n', '--dry-run', action='store_true',
                      help='Preview changes without making them')
    parser.add_argument('--all-files', action='store_true',
                      help='Process all files, not just those with non-ASCII characters')
    parser.add_argument('--backup', action='store_true',
                      help='Create backup mapping file for restoration')
    parser.add_argument('--force', action='store_true',
                      help='Force normalization even if target filename exists')
    parser.add_argument('-q', '--quiet', action='store_true',
                      help='Suppress detailed output')
    parser.add_argument('--stats-only', action='store_true',
                      help='Show statistics without making changes')
    
    args = parser.parse_args()
    
    print("🌍 Universal NFD to NFC Filename Normalizer")
    print("==========================================")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    elif args.stats_only:
        print("📊 STATISTICS ONLY MODE")
    
    print()
    
    try:
        normalizer = UniversalNFCNormalizer(
            directory=args.directory,
            dry_run=args.dry_run,
            all_files=args.all_files,
            backup=args.backup,
            force=args.force,
            quiet=args.quiet,
            stats_only=args.stats_only
        )
        normalizer.run()
        
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()