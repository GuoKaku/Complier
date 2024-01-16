define i32 @"main"()
{
entry:
  %".2" = getelementptr inbounds [53 x i8], [53 x i8]* @".str0", i32 0, i32 0
  %".3" = call i32 (i8*, ...) @"printf"(i8* %".2")
  %"ch" = alloca i8
  %"count" = alloca i32
  store i32 0, i32* %"count"
  %"list" = alloca [100 x i32]
  %".5" = getelementptr inbounds [3 x i8], [3 x i8]* @".str1", i32 0, i32 0
  %".6" = load i32, i32* %"count"
  %".7" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".6"
  %".8" = call i32 (i8*, ...) @"scanf"(i8* %".5", i32* %".7")
  %".9" = load i32, i32* %"count"
  %".10" = add i32 %".9", 1
  store i32 %".10", i32* %"count"
  %".12" = getelementptr inbounds [3 x i8], [3 x i8]* @".str2", i32 0, i32 0
  %".13" = call i32 (i8*, ...) @"scanf"(i8* %".12", i8* %"ch")
  br label %".14"
.14:
  %".18" = load i8, i8* %"ch"
  %".19" = icmp ne i8 %".18", 10
  %".20" = icmp ne i1 %".19", 0
  br i1 %".20", label %".15", label %".16"
.15:
  %".22" = getelementptr inbounds [3 x i8], [3 x i8]* @".str3", i32 0, i32 0
  %".23" = load i32, i32* %"count"
  %".24" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".23"
  %".25" = call i32 (i8*, ...) @"scanf"(i8* %".22", i32* %".24")
  %".26" = load i32, i32* %"count"
  %".27" = add i32 %".26", 1
  store i32 %".27", i32* %"count"
  %".29" = getelementptr inbounds [3 x i8], [3 x i8]* @".str4", i32 0, i32 0
  %".30" = call i32 (i8*, ...) @"scanf"(i8* %".29", i8* %"ch")
  br label %".14"
.16:
  %"temp" = alloca i32
  %"j" = alloca i32
  %"i" = alloca i32
  store i32 1, i32* %"i"
  br label %".33"
.33:
  %".37" = load i32, i32* %"i"
  %".38" = load i32, i32* %"count"
  %".39" = icmp slt i32 %".37", %".38"
  %".40" = icmp ne i1 %".39", 0
  br i1 %".40", label %".34", label %".35"
.34:
  store i32 0, i32* %"j"
  br label %".43"
.35:
  store i32 0, i32* %"i"
  br label %".90"
.43:
  %".47" = load i32, i32* %"j"
  %".48" = load i32, i32* %"count"
  %".49" = load i32, i32* %"i"
  %".50" = sub i32 %".48", %".49"
  %".51" = icmp slt i32 %".47", %".50"
  %".52" = icmp ne i1 %".51", 0
  br i1 %".52", label %".44", label %".45"
.44:
  %".54" = load i32, i32* %"j"
  %".55" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".54"
  %".56" = load i32, i32* %".55"
  %".57" = load i32, i32* %"j"
  %".58" = add i32 %".57", 1
  %".59" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".58"
  %".60" = load i32, i32* %".59"
  %".61" = icmp sgt i32 %".56", %".60"
  %".62" = icmp ne i1 %".61", 0
  br i1 %".62", label %".44.if", label %".44.endif"
.45:
  %".85" = load i32, i32* %"i"
  %".86" = add i32 %".85", 1
  store i32 %".86", i32* %"i"
  br label %".33"
.44.if:
  %".64" = load i32, i32* %"j"
  %".65" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".64"
  %".66" = load i32, i32* %".65"
  store i32 %".66", i32* %"temp"
  %".68" = load i32, i32* %"j"
  %".69" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".68"
  %".70" = load i32, i32* %"j"
  %".71" = add i32 %".70", 1
  %".72" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".71"
  %".73" = load i32, i32* %".72"
  store i32 %".73", i32* %".69"
  %".75" = load i32, i32* %"j"
  %".76" = add i32 %".75", 1
  %".77" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".76"
  %".78" = load i32, i32* %"temp"
  store i32 %".78", i32* %".77"
  br label %".44.endif"
.44.endif:
  %".81" = load i32, i32* %"j"
  %".82" = add i32 %".81", 1
  store i32 %".82", i32* %"j"
  br label %".43"
.90:
  %".94" = load i32, i32* %"i"
  %".95" = load i32, i32* %"count"
  %".96" = icmp slt i32 %".94", %".95"
  %".97" = icmp ne i1 %".96", 0
  br i1 %".97", label %".91", label %".92"
.91:
  %".99" = getelementptr inbounds [4 x i8], [4 x i8]* @".str5", i32 0, i32 0
  %".100" = load i32, i32* %"i"
  %".101" = getelementptr inbounds [100 x i32], [100 x i32]* %"list", i32 0, i32 %".100"
  %".102" = load i32, i32* %".101"
  %".103" = call i32 (i8*, ...) @"printf"(i8* %".99", i32 %".102")
  %".104" = load i32, i32* %"i"
  %".105" = add i32 %".104", 1
  store i32 %".105", i32* %"i"
  br label %".90"
.92:
  ret i32 0
}

@".str0" = constant [53 x i8] c"Please enter a line of integers separated by spaces\0a\00"
declare i32 @"printf"(i8* %".1", ...)

@".str1" = constant [3 x i8] c"%d\00"
declare i32 @"scanf"(i8* %".1", ...)

@".str2" = constant [3 x i8] c"%c\00"
@".str3" = constant [3 x i8] c"%d\00"
@".str4" = constant [3 x i8] c"%c\00"
@".str5" = constant [4 x i8] c"%d \00"
