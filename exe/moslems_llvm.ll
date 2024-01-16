define i32 @"main"()
{
entry:
  %"i" = alloca i32
  store i32 0, i32* %"i"
  %"n" = alloca i32
  store i32 0, i32* %"n"
  %"a" = alloca [2048 x i8]
  %".4" = getelementptr inbounds [23 x i8], [23 x i8]* @".str0", i32 0, i32 0
  %".5" = call i32 (i8*, ...) @"printf"(i8* %".4")
  %".6" = getelementptr inbounds [2048 x i8], [2048 x i8]* %"a", i32 0, i32 0
  %".7" = call i32 (...) @"gets"(i8* %".6")
  %".8" = getelementptr inbounds [2048 x i8], [2048 x i8]* %"a", i32 0, i32 0
  %".9" = call i32 @"strlen"(i8* %".8")
  store i32 %".9", i32* %"n"
  br label %".11"
.11:
  %".15" = load i32, i32* %"i"
  %".16" = load i32, i32* %"n"
  %".17" = icmp slt i32 %".15", %".16"
  %".18" = icmp ne i1 %".17", 0
  br i1 %".18", label %".12", label %".13"
.12:
  %".20" = load i32, i32* %"i"
  %".21" = getelementptr inbounds [2048 x i8], [2048 x i8]* %"a", i32 0, i32 %".20"
  %".22" = load i8, i8* %".21"
  %".23" = load i32, i32* %"n"
  %".24" = load i32, i32* %"i"
  %".25" = sub i32 %".23", %".24"
  %".26" = sub i32 %".25", 1
  %".27" = getelementptr inbounds [2048 x i8], [2048 x i8]* %"a", i32 0, i32 %".26"
  %".28" = load i8, i8* %".27"
  %".29" = icmp ne i8 %".22", %".28"
  %".30" = icmp ne i1 %".29", 0
  br i1 %".30", label %".12.if", label %".12.endif"
.13:
  %".39" = getelementptr inbounds [43 x i8], [43 x i8]* @".str2", i32 0, i32 0
  %".40" = call i32 (i8*, ...) @"printf"(i8* %".39")
  ret i32 0
.12.if:
  %".32" = getelementptr inbounds [47 x i8], [47 x i8]* @".str1", i32 0, i32 0
  %".33" = call i32 (i8*, ...) @"printf"(i8* %".32")
  ret i32 0
.12.endif:
  %".35" = load i32, i32* %"i"
  %".36" = add i32 %".35", 1
  store i32 %".36", i32* %"i"
  br label %".11"
}

@".str0" = constant [23 x i8] c"Please enter a string\0a\00"
declare i32 @"printf"(i8* %".1", ...)

declare i32 @"gets"(...)

declare i32 @"strlen"(i8* %".1")

@".str1" = constant [47 x i8] c"this string is not a language of the Moslems.\0a\00"
@".str2" = constant [43 x i8] c"this string is a language of the Moslems.\0a\00"
