package betterwoodchests.modid;

import java.util.LinkedHashMap;
import java.util.Map;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.NoteBlockInstrument;
import net.minecraft.world.level.material.MapColor;

public class ModBlocks {
    public static final String[] WOODS = {
        "oak", "spruce", "birch", "jungle", "acacia", "dark_oak",
        "mangrove", "cherry", "pale_oak", "bamboo", "crimson", "warped"
    };
    public static final Map<String, Block> CHESTS = new LinkedHashMap<>();
    public static final Map<String, Item> CHEST_ITEMS = new LinkedHashMap<>();

    static {
        for (String wood : WOODS) {
            Identifier id = Identifier.fromNamespaceAndPath(BetterWoodChests.MOD_ID, wood + "_chest");
            BlockBehaviour.Properties props = BlockBehaviour.Properties.of()
                .mapColor(MapColor.WOOD)
                .instrument(NoteBlockInstrument.BASS)
                .strength(2.5F)
                .sound(SoundType.WOOD)
                .setId(ResourceKey.create(Registries.BLOCK, id));
            Block block = Registry.register(BuiltInRegistries.BLOCK, id,
                new ChestBlock(() -> ModBlockEntities.WOOD_CHEST,
                    SoundEvents.CHEST_OPEN, SoundEvents.CHEST_CLOSE, props));
            Item item = Registry.register(BuiltInRegistries.ITEM, id,
                new BlockItem(block, new Item.Properties()
                    .setId(ResourceKey.create(Registries.ITEM, id))
                    .useBlockDescriptionPrefix()));
            CHESTS.put(wood, block);
            CHEST_ITEMS.put(wood, item);
        }
    }

    public static Block[] chestArray() {
        return CHESTS.values().toArray(new Block[0]);
    }

    public static void init() {}
}
