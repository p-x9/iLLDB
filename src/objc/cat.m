@import Foundation;
@import CoreFoundation;

// #import <CoreFoundation/CoreFoundation.h>
// #import <Foundation/Foundation.h>

NSString *path = @"<FILE_PATH>";
NSString *mode = @"<MODE>";

NSFileManager *fileManager = [NSFileManager defaultManager];

BOOL isDirectory = NO;
BOOL exists = [fileManager fileExistsAtPath:path isDirectory:&isDirectory];

if (!exists) {
  printf("`%s` is not existed", (char *)[path UTF8String]);
} else if (isDirectory) {
  printf("`%s` is a directory", (char *)[path UTF8String]);
} else {
  if ([mode isEqualToString:@"plist"]) {
    CFURLRef fileURL = CFURLCreateWithFileSystemPath(
        kCFAllocatorDefault, (CFStringRef)path, kCFURLPOSIXPathStyle, false);
    CFReadStreamRef stream =
        CFReadStreamCreateWithFile(kCFAllocatorDefault, fileURL);
    CFReadStreamOpen(stream);

    CFPropertyListRef plist = CFPropertyListCreateWithStream(
        kCFAllocatorDefault, stream, 0, kCFPropertyListImmutable, NULL, NULL);

    if (CFGetTypeID(plist) == CFDictionaryGetTypeID()) {
      NSDictionary *plistDictionary = (__bridge NSDictionary *)plist;
      printf("%s\n", (char *)[[plistDictionary description] UTF8String]);
    } else {
      printf("cannot loaded");
    }
    CFRelease(plist);
    CFReadStreamClose(stream);
    CFRelease(stream);
    CFRelease(fileURL);

  } else {
    NSError *error = nil;
    NSString *fileContents =
        [NSString stringWithContentsOfFile:path
                                  encoding:NSUTF8StringEncoding
                                     error:&error];
    if (fileContents) {
      printf("%s\n", (char *)[fileContents UTF8String]);
    } else {
      printf("%s\n", (char *)[[error localizedDescription] UTF8String]);
    }
  }
}
